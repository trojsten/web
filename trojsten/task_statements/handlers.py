from celery.signals import task_success


@task_success.connect
def task_success(sender=None, result=None, **kwargs):
    print('task_success for task {sender} with result {result}'.format(
        sender=sender,
        result=result,
    ))
