from celery import Task
from django.db import connection, transaction


class PostTransactionTask(Task):
    """A task whose execution is delayed until after the current transaction.

    The task's fate depends on the outcome of the current transaction. If it's
    committed or no changes are made in the transaction block, the task is sent
    as normal. If it's rolled back, the task is discarded.

    If transactions aren't being managed when ``apply_asyc()`` is called (if
    you're in the Django shell, for example) or the ``after_transaction``
    keyword argument is ``False``, the task will be sent immediately.

    A replacement decorator is provided:

    .. code-block:: python

        from djcelery_transactions import task

        @task
        def example(pk):
            print "Hooray, the transaction has been committed!"
    """

    def original_apply_async(self, *args, **kwargs):
        """Shortcut method to reach real implementation
        of celery.Task.apply_sync
        """
        return super(PostTransactionTask, self).apply_async(*args, **kwargs)

    def apply_async(self, *args, **kwargs):
        # Delay the task unless the client requested otherwise or transactions
        # aren't being managed (i.e. the signal handlers won't send the task).
        using = kwargs['using'] if 'using' in kwargs else None
        con = transaction.get_connection(using)

        if con.get_autocommit() or con.in_atomic_block:
            if not transaction.is_dirty():
                # Always mark the transaction as dirty
                # because we push task in queue that must be fired or discarded
                transaction.set_dirty(using=using)

            task = lambda: self.original_apply_async(*args, **kwargs)
            connection.on_commit(task)
        else:
            return self.original_apply_async(*args, **kwargs)
