from __future__ import absolute_import
import logging
import time
import socket
import uuid
import pprint
from commandRunner.localRunner import *
from commandRunner.rRunner import *
from commandRunner.pythonRunner import *

from celery import Celery
from celery import shared_task
from celery import group
from celery import chain

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.core.files.base import ContentFile

from .models import Backend, Job, Submission, Task, Result, Parameter
from .models import QueueType, BackendUser, Batch

logger = logging.getLogger(__name__)

ge_available = False
try:
    from commandRunner.geRunner import *
    ge_available = True
except Exception as e:
    logger.info("SGE_ROOT AND DRMAA_LIBRARY_PATH ARE NOT SET; " +
                "GridEngine backend not available")


@shared_task
def wait(t):
    """
        A task the waits. We'll use this for some trivial integration testing
    """
    time.sleep(t)
    return("passed")


@shared_task
def add(x, y):
    """
        The default tutorial example. Maybe use for integration testing
    """
    return x + y


# When starting a previous job we get the previous data out of the
# db
def get_data(s, uuid, current_step, in_globs):
    data_dict = {}
    data = None
    previous_step = None
    # found_set = set()
    # if this is the first task in a chain get the input_data from submission
    # if this is not the first task get the input_data from the results
    if current_step == 1:
        s.input_data.open(mode='rb')
        content = s.input_data.read()
        try:  # depending on the version of django data might reach here
                # as either a byte str or a regular str. if we were being
                # super defensive we should check line is a str
            data = content.decode(encoding='UTF-8')
        except AttributeError:
            data = content
        except UnicodeDecodeError:
            data = content
        except TypeError:
            data = content
        s.input_data.close()
        local_glob = in_globs[0].lstrip(".")
        data_dict[uuid+"."+local_glob] = data # where it gives uuid.input
    else:
        previous_step = current_step-1
        # print("DATA GETTING STEP ID"+str(previous_step))
        r = Result.objects.filter(submission=s, step__lte=previous_step).all()
        for result in r:
            # print("RESULT ID"+str(result))
            for glob in in_globs:
                # print("GLOB TO MATCH"+str(glob))
                if glob in result.result_data.name:
                    # print("FOUND A MATCH"+str(result.result_data.name)+str(glob))
                    # found_set.add(glob)
                    result.result_data.open(mode='rb')
                    content = result.result_data.read()
                    # print("OPENED DATA FILE")
                    data = None
                    # print(line)
                    try:  # depending on the version of django data might
                            # reach here as either a byte str or a str
                        data = content.decode(encoding='UTF-8')
                    except AttributeError:
                        data = content
                    except UnicodeDecodeError:
                        data = content
                    except TypeError:
                        data = content
                    data_dict[result.result_data.name] = data
                    result.result_data.close()
                    # print("GOT FILE DATA")
    # if current_step != 1:
    #     if len(in_globs) != len(found_set):
    #         raise Exception("Found set of globs not the same size as",
    #                         "requested:", str(len(in_globs)), "vs",
    #                         str(len(found_set)))

    return(data_dict, previous_step)


# we get a llist of the files and insert them in to the db
def insert_data(output_data, s, t, current_step, previous_step):
    if output_data is not None:
        # If not we trigger the No Outputs behaviour instead of pushing
        # the results to the db

        for fName, fData in output_data.items():
            # print("Writing Captured data")
            file = SimpleUploadedFile(fName, fData)
            logger.info("Result: Adding file to Results "+fName)
            r = Result.objects.create(submission=s, task=t,
                                      step=current_step, name=t.name,
                                      message='Result',
                                      previous_step=previous_step,
                                      result_data=file)
            logger.info("Result: File added")
    else:
        logger.info("Result: No files to add")
        r = Result.objects.create(submission=s, task=t,
                                  step=current_step, name=t.name,
                                  message='Result',
                                  previous_step=previous_step,
                                  result_data=None)


def build_file_globs(t):
    '''
        Not yet covered with unit tests
    '''
    in_globs = "".join(t.in_glob.split()).split(",")
    out_globs = "".join(t.out_glob.split()).split(",")

    iglob = in_globs[0].lstrip(".")
    oglob = out_globs[0].lstrip(".")
    return(in_globs, out_globs, iglob, oglob)


def make_runner(value, uuid, t, out_globs, in_globs, data_dict, params,
                param_values, stdoglob, environment, state, step_id, self,
                execution_behaviour):
    '''
        Not yet covered with unit tests
    '''
    kwargs = {'tmp_id': uuid,
              'tmp_path': t.backend.root_path,
              'out_globs': out_globs,
              'in_globs': in_globs,
              'input_data': data_dict,
              'params': params,
              'param_values': param_values,
              'identifier': uuid,
              'std_out_str': uuid+stdoglob,
              'env_vars': environment,
              'debug': False,
              }
    if settings.DEBUG:
        kwargs['debug'] = True
    if value:
        kwargs['value_string'] = value
    if execution_behaviour == QueueType.LOCALHOST:
        logger.info("Running On LOCALHOST")
        kwargs['command'] = t.executable
        return localRunner(**kwargs)
    if execution_behaviour == QueueType.GRIDENGINE:
        if ge_available:
            logger.info("Running At GRIDENGINE")
            kwargs['command'] = t.executable
            return geRunner(**kwargs)
        else:
            raise OSError("Grid Engine Libraries not available")
    if execution_behaviour == QueueType.R:
        logger.info("Running R")
        kwargs['script'] = t.executable
        return rRunner(**kwargs)
    if execution_behaviour == QueueType.PYTHON:
        logger.info("Running Python")
        kwargs['script'] = t.executable
        return pythonRunner(**kwargs)
    return None


def prepare_exit_statuses(uuid, t, state, step_id, self,
                          current_step, command, s):
    '''
        Not yet covered with unit tests
    '''
    valid_exit_status = [0, ]
    custom_exit_statuses = []

    custom_exit_map = {}
    if t.custom_success_exit is not None:
        custom_exit_map[Task.CONTINUE] = t.custom_success_exit
    if t.custom_terminate_exit is not None:
        custom_exit_map[Task.TERMINATE] = t.custom_terminate_exit
    if t.custom_fail_exit is not None:
        custom_exit_map[Task.FAIL] = t.custom_fail_exit

    if len(custom_exit_map) > 0:
        for key in custom_exit_map.keys():
            exit_code = custom_exit_map[key].replace(" ", "")
            try:
                if len(exit_code) > 0:
                    parsed_exit_code = list(map(int, exit_code.split(",")))
                    custom_exit_map[key] = parsed_exit_code
            except Exception as e:
                exit_status_message = "Exit statuses contains non-numerical and " \
                                    "other punctuation "+str(e) + \
                                    " : "+str(current_step) + " : " + command
                Submission.update_submission_state(s, True, state, step_id,
                                                self.request.id,
                                                exit_status_message,
                                                socket.gethostname())
                Batch.update_batch_state(s.batch, state)
                __handle_batch_email(s)
                logger.debug(uuid+": prepare_exit_statuses():"+exit_status_message)
                raise OSError(exit_status_message)
        
        valid_exit_status += custom_exit_map.get(Task.CONTINUE, [])
        valid_exit_status += custom_exit_map.get(Task.TERMINATE, [])

    return valid_exit_status, custom_exit_map


def handle_task_exit(exit_status, valid_exit_status, custom_exit_map,
                     run, out_globs, t, s, current_step, previous_step, self,
                     state, step_id, exit_code_file):
    '''
        Not yet covered with unit tests
    '''
    custom_exit_termination = False
    incomplete_outputs_termination = False
    if exit_status in valid_exit_status:
        # Here we test the custom exit status. And do as it requires
        # skipping the regular raise() if needed
        if exit_status in custom_exit_map.get(Task.TERMINATE, []):
            custom_exit_termination = True

        found_endings = []
        if run.output_data is not None:
            # Remove exit code from previous task as output_data, we only need it as input
            keys_to_remove = [key for key in run.output_data if key.endswith("_exit_code.txt")]

            for key in keys_to_remove:
                run.output_data.pop(key)

            for fName, fData in run.output_data.items():
                found_endings.append("."+fName.split(".")[-1])

        # Add exit code of this task execution to the results
        if len(exit_code_file) > 0:
            insert_data(exit_code_file, s, t, current_step, previous_step)
            found_endings.append("exit_code.txt")

        if set(out_globs).issubset(found_endings):
            insert_data(run.output_data, s, t, current_step, previous_step)
        else:
            if t.incomplete_outputs_behaviour == Task.FAIL:
                # insert what we have and then raise and error
                insert_data(run.output_data, s, t, current_step, previous_step)
                Submission.update_submission_state(s, True, state, step_id,
                                                   self.request.id,
                                                   "Failed with missing"
                                                   " outputs: " +
                                                   str(run.command),
                                                   socket.gethostname())
                Batch.update_batch_state(s.batch, state)
                logger.error("Failed with missing outputs: "+str(run.command))
                raise OSError("Failed with missing outputs: "+str(run.command))
            if t.incomplete_outputs_behaviour == Task.TERMINATE:
                # insert what we have and end the job gracefully
                insert_data(run.output_data, s, t, current_step, previous_step)
                if self.request.chain:
                    self.request.chain = None
                incomplete_outputs_termination = True
            if t.incomplete_outputs_behaviour == Task.CONTINUE:
                # by default we insert whatever results we have and keep going
                insert_data(run.output_data, s, t, current_step, previous_step)
    elif exit_status in custom_exit_map.get(Task.FAIL, []):
            # if we hit an exit status that we ought to fail on raise an error
        insert_data(run.output_data, s, t, current_step, previous_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id,
                                           'Failed step, non 0 exit at step:' +
                                           str(step_id),socket.gethostname())
        Batch.update_batch_state(s.batch, state)
        logger.error("Exit Status " + str(exit_status) +
                     ": Failed with custom exit status: "+str(run.command))
        raise OSError("Exit Status " + str(exit_status) +
                      ": Failed with custom exit status: "+str(run.command))
    else:
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id,
                                           'Failed step, non 0' +
                                           ' exit at step: ' +
                                           str(step_id) + ". Exit status:" +
                                           str(exit_status),
                                           socket.gethostname())
        Batch.update_batch_state(s.batch, state)
        logger.error("Exit Status " + str(exit_status) +
                     ": Command did not run: "+str(run.command))
        raise OSError("Exit Status " + str(exit_status) +
                      ": Command did not run: "+str(run.command))

    return custom_exit_termination, incomplete_outputs_termination


def __handle_batch_email(s):
    entries = Batch.objects.filter(UUID=s.batch.UUID)
    message_str = settings.EMAIL_MESSAGE_STRING+s.batch.UUID
    if entries[0].status == Batch.ERROR or entries[0].status == Batch.CRASH:
        message_str = "Job "+s.batch.UUID+" has failed\n\n" + \
                      "Please contact the server administrator with the job " \
                      "ID and the following error message\n\n"+s.last_message

    if entries[0].status == Batch.COMPLETE or entries[0].status == Batch.ERROR\
       or entries[0].status == Batch.CRASH:
        try:
            if s.email is not None and \
                    len(s.email) > 5 and \
                    settings.DEFAULT_FROM_EMAIL is not None:
                send_mail(str(s.job)+" : "+settings.EMAIL_SUBJECT_STRING+": "+s.batch.UUID,
                          message_str,
                          from_email=None,
                          recipient_list=[s.email],
                          fail_silently=False)
            logger.info("SENDING MAIL TO: "+s.email)
        except Exception as e:
            logger.info("Mail server not available:" + str(e))
        s.email = None
        # if settings.EMAIL_DELETE_AFTER_USE:
        #     s.email = None
        #     s.save()
        # print('batch not complete yet')


def __build_environment(task):
    environment = {}
    envs = task.environment.all()
    for env in envs:
        environment[env.env] = env.value
    return(environment)


def __construct_chain_string(steps, UUID, job_priority):
    """
        Function takes all the step and task information for a given job
        and returns a valid celery string
    """
    total_steps = len(steps)
    chord_end = False
    current_step = 0
    step_counter = 1
    prev_step = None
    queue_name = 'celery'
    flags = {}
    options = {}
    value = ''

    if total_steps > 1:
        if steps[total_steps-1].ordering == steps[total_steps-2].ordering:
            total_steps += 1
            chord_end = True

    task_strings = {}
    # loop over steps and build the subtask string for each
    # track which have the same step priority
    # build group() for any which have equivalent priority
    # where priority list > 1
    # insert subtask or group in to chain()()

    for step in steps:
        params = []
        param_values = {}
        value = ''
        environment = __build_environment(step.task)
        queue_name = str(step.task.backend.queue_type)
        if step.ordering != prev_step:
            current_step += 1
        
        condition = ''
        if step.condition is not None:
            condition = step.condition

        # tchain += "task_runner.si('%s',%i,%i,%i,'%s') | " \
        task_string = "task_runner.subtask(('%s', %i, %i, %i, %i, '%s', " \
                      "%s, %s, '%s', %i, %s, '%s'), " \
                      "immutable=True, queue='%s')" \
                      % (UUID,
                         step.ordering,
                         current_step,
                         step_counter,
                         total_steps,
                         step.task.name,
                         params,
                         pprint.pformat(param_values).replace('\n',''),
                         value,
                         step.task.backend.queue_type.execution_behaviour,
                         environment,
                         condition,
                         queue_name)

        if step.ordering in task_strings:
            task_strings[step.ordering].append(task_string)
        else:
            task_strings[step.ordering] = [task_string]
        prev_step = step.ordering
        step_counter += 1

    tchain = "chain("
    for key in sorted(task_strings):
        if len(task_strings[key]) > 1:
            tchain += "group("
        for task_string in task_strings[key]:
            tchain += task_string+", "
        if len(task_strings[key]) > 1:
            tchain = tchain[:-2]
            tchain += "), "
    tchain = tchain[:-2]

    # This hack means that a job which ends in a chord won't complete
    # during the chord
    if chord_end is True:
        tchain += ", chord_end.subtask(('%s', %i, %i), " \
                  "immutable=True, queue='%s')" \
                  % (UUID, current_step, total_steps, queue_name)
    tchain += ',).apply_async()'

    logger.debug("TASK COMMAND: "+tchain)
    return(tchain)



@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40,
             max_retries=5)
def task_job_runner(self, *args, **kwargs):
    masterUUID = str(uuid.uuid1())
    b = Batch.objects.create(UUID=masterUUID)

    print("Getting Job", args[0])
    try:
        job = Job.objects.get(name=args[0])
        if job:
            steps = job.steps.all().select_related('task') \
                    .extra(order_by=['ordering'])
            s = Submission()
            s.priority = settings.DEFAULT_JOB_PRIORITY
            s.UUID = str(uuid.uuid1())
            s.email = settings.ADMIN_EMAIL
            s.batch = b
            s.input_data.save("dummy.txt", ContentFile("empty"))
            s.job = job
            s.save()

            tchain = __construct_chain_string(steps, s.UUID,
                                              settings.DEFAULT_JOB_PRIORITY)
            #print(tchain)
            try:
                logger.info('Sending this chain: '+tchain)
                exec(tchain)
            except SyntaxError:
                logger.error('SyntaxError: Invalid string exec on: ' + tchain)
            except Exception as e:
                logger.error('500 Error: Invalid string exec on: ' + tchain)
                logger.error('500 Error' + str(e))
    except Job.DoesNotExist:
        pass



# time limits?
# step_id is the numerical value the user provides when they set the steps
#         in the UI
# current_step is a counter of where in the process we are, celery groups take
#              the same step value, which allows a subsequent step to get all
#              the results from the group
# step_counter a counter which counts which step this is in sequence used in
#              conjunction with total_steps to tell when a job has finished
# total_step   a total of all the units of work/tasks that a job has
@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40,
             max_retries=5)
def task_runner(self, uuid, step_id, current_step, step_counter,
                total_steps, task_name, params, param_values, value,
                execution_behaviour, environment, condition):
    """
        Here is the action. Takes and task name and a job UUID. Gets the task
        config from the db and the job data and runs the job.
        Also needs to give control to whichever library supports the backend
        in question.
        Once the data is on the backend this task then just watches the
        backend until the job is done.d
        Results are pushed to the frontend db but because they are files
        we just use the celery results for messaging and the results table
        for the files
    """
    logger.info("TASK:" + task_name)
    logger.info("CURRENT STEP:" + str(current_step))
    logger.info("TOTAL STEPS:" + str(total_steps))
    logger.info("STEP ID:" + str(step_id))

    # prepare all objects and parameters for commandRunner.
    s = Submission.objects.get(UUID=uuid)
    t = Task.objects.get(name=task_name)
    # b = Batch.objects.get()
    state = Submission.ERROR
    logger.info("BUILDING GLOBS:" + str(step_id))
    in_globs, out_globs, iglob, oglob = build_file_globs(t)
    logger.info("GETTING PREVIOUS DATA:" + str(step_id))
    data_dict, previous_step = get_data(s, uuid, current_step, in_globs)
    logger.info("IN_GLOB:" + str(in_globs))
    logger.info("DATA_DICT:" + str(data_dict))
    logger.info("SETTING STDOUT GLOB:" + str(step_id))
    stdoglob = ".stdout"
    if t.stdout_glob is not None and len(t.stdout_glob) > 0:
        stdoglob = "."+t.stdout_glob.lstrip(".")
    
    # Handle BatchRequirements
    handle_batch_requirements(t.requirements, t.backend.root_path)

    #handle the task initial_workdir_requirement
    handle_initial_workdir_requirement(t.requirements,str(step_id),t.backend.root_path)
    
    #check the software requirement version
    check_software_requirement(t.requirements)


    # Handle "when" condition
    logger.info("CONDITION:" + str(condition))
    if condition != '':
        exit_code = data_dict.get(str(uuid)+"_"+str(step_counter-1)+'_exit_code.txt', None)
        if exit_code is not None:
            if 'exit_code' in condition:
                exit_code = int(exit_code)
                continue_task = eval(condition)
                if not continue_task:
                    Submission.update_submission_state(s, True, Submission.RUNNING,
                                               step_id,
                                               self.request.id,
                                               'Skipping step: ' +
                                               str(current_step),
                                               socket.gethostname())
                    if step_counter == total_steps:
                        state = Submission.COMPLETE
                        Submission.update_submission_state(s, True, state,
                                               step_id,
                                               self.request.id,
                                               'Completed job at step # ' +
                                               str(current_step-1),
                                               socket.gethostname())
                        
                        batch_subs = Submission.objects.filter(batch=s.batch)
                        complete_count = 0
                        for sub in batch_subs:
                            if sub.status == Submission.COMPLETE:
                                complete_count += 1
                        if complete_count == len(batch_subs):
                            if s.batch.status != Batch.ERROR and s.batch.status != Batch.CRASH:
                                Batch.update_batch_state(s.batch, state)
                    return
        else:
            state = Submission.ERROR
            Submission.update_submission_state(s, True, state, step_id,
                                                   self.request.id,
                                                   "Failed with missing"
                                                   " outputs: exit_code from previous step",
                                                   socket.gethostname())
            Batch.update_batch_state(s.batch, state)
            logger.error("Failed with missing outputs: exit_code from previous step")
            raise OSError("Failed with missing outputs: exit_code from previous step")

    # update submission tracking to note that this is running
    logger.info("SETTING RUN FLAG:" + str(step_id))
    with transaction.atomic():
        if s.status != Submission.ERROR and s.status != Submission.CRASH:
            Submission.update_submission_state(s, True, Submission.RUNNING,
                                               step_id,
                                               self.request.id,
                                               'Running step: ' +
                                               str(current_step),
                                               socket.gethostname())
            Batch.update_batch_state(s.batch, Batch.RUNNING)

    # Now we run the task handing off the actual running to the commandRunner
    # library
    run = None
    # Here we get the users list and decide which one to submit the job with
    # TODO: Candidate to move to the command runner as it should handle the
    # finding out what is happening on the backend. Perhaps API call in
    # which returns the number of running processes and maybe the load average

    # Initialise commandRunner here
    try:
        run = make_runner(value, uuid, t, out_globs, in_globs, data_dict,
                          params, param_values, stdoglob, environment, state,
                          step_id, self, execution_behaviour)
    # print(vars(run))
    except Exception as e:
        cr_message = "Unable to initialise commandRunner: "+str(e)+" : " + \
                      str(current_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, cr_message,
                                           socket.gethostname())
        Batch.update_batch_state(s.batch, state)
        logger.debug(uuid+": make_runner(): "+cr_message)
        __handle_batch_email(s)
        raise OSError(cr_message)

    # prepare the temp working directory here
    try:
        run.prepare()
    except Exception as e:
        prep_message = "Unable to prepare files and tmp directory: "+str(e) + \
                       " : "+str(current_step)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, prep_message,
                                           socket.gethostname())
        Batch.update_batch_state(s.batch, state)
        logger.debug(uuid+": run.prepare(): "+prep_message)
        __handle_batch_email(s)
        raise OSError(prep_message)
    # print(vars(run))
    # set the valid exit statuses in case their is a defined value alternative
    valid_exit_status, custom_exit_map = prepare_exit_statuses(uuid, t,
                                                                    state,
                                                                    step_id,
                                                                    self,
                                                                    current_step,
                                                                    run.command,
                                                                    s)

    # execute the command
    try:
        logger.info("STD OUT: "+run.std_out_str)
        logger.info("EXIT STATUSES: "+str(valid_exit_status))
        if hasattr(run, 'command'):
            logger.info("EXECUTABLE: "+run.command)
            exit_status = run.run_cmd(valid_exit_status)
        if hasattr(run, 'script'):
            logger.info("SCRIPT: "+run.script)
            exit_status = run.run_cmd()
    except Exception as e:
        if hasattr(run, 'command'):
            run_message = "Unable to call commandRunner.run_cmd(): "+str(e) + \
                           " : "+str(current_step) + " : " + run.command
            __handle_batch_email(s)
        if hasattr(run, 'script'):
            run_message = "Unable to call commandRunner.run_cmd(): "+str(e) + \
                           " : "+str(current_step) + " : WITH SCRIPT"
            __handle_batch_email(s)
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, run_message,
                                           socket.gethostname())
        Batch.update_batch_state(s.batch, state)
        logger.debug(uuid+": run.run_cmd(): "+run_message)
        # We don't raise and error here as we want to test the exit status
        # and make a decision later
        __handle_batch_email(s)
        raise OSError(run_message)
    
    # Collect this task exit code and save it to the result if exit code is the output in cwl
    exit_code_file = {}
    if 'exit_code.txt' in t.out_glob:
        exit_code_file = {
            str(uuid) + '_' + str(step_counter) + '_exit_code.txt': str(exit_status).encode('utf-8'),
        }

    # if the command ran with success we'll send the file contents to the
    # database.
    # TODO: For now we write everything to the file as utf-8 but we'll need to
    # handle binary data eventually

    # if DEBUG settings are true we leave behind the temp working dir.
    if settings.DEBUG is not True:
        run.tidy()

    # now the job has run handle getting results and what happens with differen
    # exit statusesd or outputs
    custom_exit_termination,\
        incomplete_outputs_termination = handle_task_exit(exit_status,
                                                          valid_exit_status,
                                                          custom_exit_map,
                                                          run, out_globs, t, s,
                                                          current_step,
                                                          previous_step, self,
                                                          state, step_id, exit_code_file)

    # decide if we should complete the job
    complete_job = False
    if custom_exit_termination:
        complete_job = True
        logger.debug(uuid+": completing job due to custom exit: " +
                     str(custom_exit_map.get(Task.TERMINATE, [])))
    if incomplete_outputs_termination:
        complete_job = True
        logger.debug(uuid+": completing job due to incomplete outputs")

    if step_counter == total_steps:
        complete_job = True
        logger.debug(uuid+": completing job due to final step: " +
                     str(step_counter)+"=="+str(total_steps))

    # Update where we are in the steps to the submission table
    state = Submission.RUNNING
    message = "Completed step: " + str(current_step)
    if complete_job:
        state = Submission.COMPLETE
        message = 'Completed job at step #' + str(current_step)
        # TODO: This needs a try-catch

    # s2 = Submission.objects.get(UUID=uuid)
    # send message to frontend now the task is run and the results are handled
    s.refresh_from_db()
    if s.status != Submission.ERROR and s.status != Submission.CRASH:
        Submission.update_submission_state(s, True, state, step_id,
                                           self.request.id, message,
                                           socket.gethostname())

    batch_subs = Submission.objects.filter(batch=s.batch)
    complete_count = 0
    for sub in batch_subs:
        if sub.status == Submission.COMPLETE:
            complete_count += 1
    if complete_count == len(batch_subs):
        if s.batch.status != Batch.ERROR and s.batch.status != Batch.CRASH:
            Batch.update_batch_state(s.batch, state)

    __handle_batch_email(s)
    # if we need to terminate the chain send that signal here
    if len(custom_exit_map) > 0:
        if exit_status in custom_exit_map.get(Task.TERMINATE, []):
            if self.request.chain:
                # print("hi there")
                self.request.chain = None


@shared_task(bind=True, default_retry_delay=5 * 60, rate_limit=40)
def chord_end(self, uuid, step_id, current_step):
    try:
        # Get the Submission from the database
        s = Submission.objects.get(UUID=uuid)
        state = Submission.COMPLETE
        message = f'Completed job at step #{current_step}'

        s.refresh_from_db()

        # Refresh the object to ensure you get the latest state
        if s.status not in [Submission.ERROR, Submission.CRASH]:
            Submission.update_submission_state(s, True, state, step_id,
                                               self.request.id, message,
                                               socket.gethostname())
        
        # Update Batch status
        Batch.update_batch_state(s.batch, state)
        
        # Process batch email notifications
        __handle_batch_email(s)

        # Record successful completion information
        logger.info(f'Chord end for UUID: {uuid}, Step ID: {step_id}, Current Step: {current_step}')
    
    except Submission.DoesNotExist:
        logger.error(f'Submission with UUID {uuid} does not exist.')
    except Exception as e:
        Catch other potential exceptions and log error messages
        logger.error(f'Error in chord_end task: {e}')
        __handle_batch_email(s)  # Ensure that notifications are also sent when errors occur


@shared_task
def handle_initial_workdir_requirement(requirements,step_id,src):
    if requirements is None:
        return f"No initial workdir setup in this step"
    initial_workdir_requirement = next((req for req in requirements if req['class'] == 'InitialWorkDirRequirement'), None)
    
    if initial_workdir_requirement:
        listing = initial_workdir_requirement.get('listing', [])
        
        for item in listing:
            if item['class'] == 'File':
                if 'entryname' in item and 'entry' in item:
                    dst = os.path.join(src, item['entryname'])
                    logging.info(f"Writing to file: {dst}")
                    try:
                        with open(dst, 'w') as f:
                            f.write(item['entry'])
                        logging.info(f"Successfully wrote to {dst}")
                    except Exception as e:
                        logging.error(f"Failed to write to {dst}: {e}")

    logger.info("Step id "+ step_id + ":Initial workdir setup completed")

@shared_task
def check_software_requirement(requirements):
    if requirements is None:
        return f"No software_requirement in this step"
    software_requirement = next((req for req in requirements if req['class'] == 'SoftwareRequirement'), None)
    
    if software_requirement:
        packages = software_requirement.get('packages', [])
        
        for package in packages:
            package_name = package.get('name')
            package_version = package.get('version')
            
            if not package_name:
                continue
            
            # Check if the package is installed
            try:
                result = subprocess.run([package_name, '--version'], capture_output=True, text=True)
                installed_version = result.stdout.strip()
                
                if package_version and package_version not in installed_version:
                    raise RuntimeError(f"Package {package_name} version {package_version} is required, but version {installed_version} is installed.")
            except FileNotFoundError:
                raise RuntimeError(f"Package {package_name} is required but not installed.")
    
    logger.info("Software requirements are satisfied.")

@shared_task
def handle_batch_requirements(task_requirements, backend_root_path):
    """
    Handle the BatchRequirement configuration and apply it to the task.
    ​:param task_requirements: task requirements, including BatchRequirement
    :param backend_root_path: indicates the root path of the batch system
    :return: None
    """
    logger.info("Handling BatchRequirements...")

    batch_requirements = [req for req in task_requirements if req.get('class') == 'BatchRequirement']
    
    if not batch_requirements:
        logger.info("No BatchRequirement found.")
        return
    
    for req in batch_requirements:
        logger.info(f"BatchRequirement found: {req}")
        batch_system = req.get('batchSystem')
        job_submission_options = req.get('jobSubmission', {})
        script_name = req.get('script', 'default_script.sh')
        
        if batch_system:
            logger.info(f"Batch system: {batch_system}")
            logger.info(f"Job submission options: {job_submission_options}")
            # Generate the path to the script
            script_path = os.path.join(backend_root_path, script_name)
            logger.info(f"Script path: {script_path}")

            # handle different batch systems
            if batch_system == 'slurm':
                handle_slurm_requirements(job_submission_options, backend_root_path, script_path)
            elif batch_system == 'pbs':
                handle_pbs_requirements(job_submission_options, backend_root_path, script_path)
            elif batch_system == 'sge':
                handle_sge_requirements(job_submission_options, backend_root_path, script_path)
            else:
                logger.warning(f"Unsupported batch system: {batch_system}")
        else:
            logger.warning("Batch system not specified in BatchRequirement.")

@shared_task
def handle_slurm_requirements(options, root_path, script_path):
    """
    Handle SLURM-related batch processing requirements.
​    :param options: job submission options
    :param root_path: root path of the batch system
    """
    logger.info(f"Configuring SLURM with options: {options} and root path: {root_path}")
    # Add specific SLURM configuration code here
    job_name = options.get('jobName', 'default_job_name')
    output_file = options.get('outputFile', 'slurm_output.txt')
    error_file = options.get('errorFile', 'slurm_error.txt')
    partition = options.get('partition', 'default')
    nodes = options.get('nodes', 1)
    ntasks = options.get('ntasks', 1)
    time_limit = options.get('time', '01:00:00')
    memory = options.get('memory', '1G')

    # Create the SLURM job script
    slurm_script = f"""#!/bin/bash
    #SBATCH --job-name={job_name}
    #SBATCH --output={output_file}
    #SBATCH --error={error_file}
    #SBATCH --partition={partition}
    #SBATCH --nodes={nodes}
    #SBATCH --ntasks={ntasks}
    #SBATCH --time={time_limit}
    #SBATCH --mem={memory}

    # Load any necessary modules
    # module load ...

    # Run the command or script
    {script_path}
    """

    # Save the SLURM job script to a file
    script_path = f"{root_path}/slurm_job_script.sh"
    with open(script_path, 'w') as script_file:
        script_file.write(slurm_script)
    
    logger.info(f"SLURM job script created at: {script_path}")
    
    # Submit the job to SLURM
    try:
        submission_command = f"sbatch {script_path}"
        submission_result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"SLURM job submitted successfully. Output: {submission_result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting SLURM job: {e.stderr}")
        raise

@shared_task
def handle_pbs_requirements(options, root_path, script_path):
    """
    Handle PBS-related batch processing requirements.
    :param options: job submission options
    :param root_path: root path of the batch system
    """
    logger.info(f"Configuring PBS with options: {options} and root path: {root_path}")
    # Add specific PBS configuration code here
    
    job_name = options.get('jobName', 'default_job_name')
    output_file = options.get('outputFile', 'pbs_output.txt')
    error_file = options.get('errorFile', 'pbs_error.txt')
    queue = options.get('queue', 'default')
    nodes = options.get('nodes', 1)
    ppn = options.get('ppn', 1)  # Number of processors per node
    time_limit = options.get('time', '01:00:00')
    memory = options.get('memory', '1gb')

    # Define the name of the pbs job script
    script_name = 'pbs_job_script.sh'
    script_path = f"{root_path}/{script_name}"

    # Create the PBS job script
    pbs_script = f"""#!/bin/bash
    #PBS -N {job_name}
    #PBS -o {output_file}
    #PBS -e {error_file}
    #PBS -q {queue}
    #PBS -l nodes={nodes}:ppn={ppn}
    #PBS -l walltime={time_limit}
    #PBS -l mem={memory}

    # Load any necessary modules
    # module load ...

    # Move to the directory where the job was submitted
    cd $PBS_O_WORKDIR

    # Run the command or script
    {script_path}
    """

    # Save the PBS job script to a file
    script_path = f"{root_path}/pbs_job_script.sh"
    with open(script_path, 'w') as script_file:
        script_file.write(pbs_script)
    
    logger.info(f"PBS job script created at: {script_path}")
    
    # Submit the job to PBS
    try:
        submission_command = f"qsub {script_path}"
        submission_result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"PBS job submitted successfully. Output: {submission_result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting PBS job: {e.stderr}")
        raise

@shared_task
def handle_sge_requirements(options, root_path, script_path):
    """
    Handle SGE related batch processing requirements.
    ​:param options: job submission options
    :param root_path: root path of the batch system
    """
    logger.info(f"Configuring SGE with options: {options} and root path: {root_path}")
    # Add specific SGE configuration code here

    job_name = options.get('jobName', 'default_job_name')
    output_file = options.get('outputFile', 'sge_output.txt')
    error_file = options.get('errorFile', 'sge_error.txt')
    queue = options.get('queue', 'default')
    parallel_env = options.get('parallelEnv', 'default')
    nodes = options.get('nodes', 1)
    ppn = options.get('ppn', 1)  # Number of processors per node
    time_limit = options.get('time', '01:00:00')
    memory = options.get('memory', '1gb')

    # Create the SGE job script
    sge_script = f"""#!/bin/bash
    #$ -N {job_name}
    #$ -o {output_file}
    #$ -e {error_file}
    #$ -q {queue}
    #$ -pe {parallel_env} {nodes}
    #$ -l h_rt={time_limit}
    #$ -l mem_free={memory}

    # Load any necessary modules
    # module load ...

    # Move to the directory where the job was submitted
    cd $SGE_O_WORKDIR

    # Run the command or script
    {script_path}
    """

    # Save the SGE job script to a file
    script_path = f"{root_path}/sge_job_script.sh"
    with open(script_path, 'w') as script_file:
        script_file.write(sge_script)
    
    logger.info(f"SGE job script created at: {script_path}")
    
    # Submit the job to SGE
    try:
        submission_command = f"qsub {script_path}"
        submission_result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"SGE job submitted successfully. Output: {submission_result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting SGE job: {e.stderr}")
        raise