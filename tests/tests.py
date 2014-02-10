from __future__ import absolute_import

from celery.registry import tasks
from celery import Celery

from django.test import TransactionTestCase
from django.conf import settings
from django.db import transaction

from djcelery_transactions import PostTransactionTask

celery = Celery('oxygen')

celery.config_from_object(settings)
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

task = celery.task

my_global = []

marker = object()


@task(base=PostTransactionTask)
def my_task():
    my_global.append(marker)

tasks.register(my_task)


class SpecificException(Exception):
    pass


class DjangoCeleryTestCase(TransactionTestCase):
    """Test djcelery transaction safe task manager
    """

    def tearDown(self):
        my_global[:] = []

    @transaction.commit_manually
    def test_commited_transaction_fire_task(self):
        """Check that task is consumed when no exception happens
        """

        def do_something():
            my_task.delay()

        do_something()
        self.assertTrue(my_global[0] is marker)

    def test_rollbacked_transaction_discard_task(self):
        """Check that task is not consumed when exception happens
        """

        def do_something():
            my_task.delay()
            raise SpecificException
        try:
            do_something()
        except SpecificException:
            self.assertTrue(my_global)
        else:
            self.fail('Exception not raised')
