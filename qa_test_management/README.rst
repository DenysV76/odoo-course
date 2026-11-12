==================
QA Test Management
==================

Test cases, requirements and test runs for the QA team, inside the same Odoo
database as the system under test. A test run belongs to a project task, holds
one line per test case and moves through Draft, In Progress and Done by buttons.
Every line gets a binary result: Pass or Fail.

.. contents::
   :local:

Business process
================

#. A QA lead keeps the reference data: functional areas and tags.
#. Requirements (acceptance criteria) and test cases are linked many-to-many.
   The *Not Covered* filter lists requirements without any test case.
#. A tester creates a test run for a task and adds test cases to it.
#. **Start** moves the run to *In Progress*; now every line gets Pass or Fail.
   A failed line must have a comment.
#. **Done** closes the run. The verdict is *Fail* as soon as one line failed.
#. **Retest Failed** opens a wizard that creates a new run with the failed
   cases only. **Print > Test Run Report** gives a PDF, one page per run.

Allowed transitions::

    draft --Start--> in_progress --Done--> done
      |                  |
      +----Cancel--------+---> cancel --Reset to Draft--> draft

Any other jump (for example draft -> done) is refused with a message.

Models
======

==========================  ==================================================
Model                       Purpose
==========================  ==================================================
``qa.test.run``             Process model: a test run of a task, with states
``qa.test.run.line``        Child model: one test case in one run, the result
``qa.functional.area``      Reference: area of a case or requirement, 2 levels
``qa.tag``                  Reference: free labels for test cases
``qa.test.case``            Test case: steps, expected result, run history
``qa.requirement``          Requirement: acceptance criterion, coverage
``qa.retest.wizard``        Wizard: retest the failed cases of a run
==========================  ==================================================

Extended standard models:

* ``project.task``: *Test Runs* smart button, *QA* tab with the verdict of the
  latest finished run and the requirements of the task.
* ``res.users``: *Open Test Runs* smart button with the runs assigned to the user.

Access rights
=============

Two groups in the *Quality Assurance* section of user settings:

* **Tester** sees and works on the test runs assigned to them; reads functional
  areas and tags; creates test cases and requirements, cannot delete them.
* **QA Lead** includes Tester, sees all runs, keeps the reference data and can
  delete records.

The source specification says "everybody sees everything". The course requires
a record rule that really restricts something, so the tester is limited to own
runs on purpose: the lead assigns the work, the tester sees their queue.

Demo users (password = login): ``qa_tester``, ``qa_tester2`` (Tester) and
``qa_lead`` (QA Lead).

Invariant
=========

**A finished test run has lines, and every line has a result.** It is guarded
by the state machine and by ``@api.constrains("state", "line_ids")`` on the run:
the Done button only moves the state, while the constraint fires on any write,
including imports and RPC calls that never press the button. A database
constraint cannot express it, because the check spans another table (the
lines). On top of that, ``UNIQUE(run_id, case_id)`` at the database level
keeps a case from appearing twice in one run even with concurrent writes, and
lines of a done or cancelled run cannot be changed or deleted, so the result
stays history.

Work map
========

====  ======================  ===========================================  ======================================================================
#     Requirement             Where                                        What exactly
====  ======================  ===========================================  ======================================================================
1     Models                  ``models/qa_test_run.py`` and 5 more         Run (process, states by buttons), run line (child), area and tag (reference), case, requirement
2     Views                   ``views/qa_test_run_views.xml``              List and form for every model; kanban of runs by state; pivot and graph of results; search views
3     Menu                    ``views/qa_menu.xml``                        Top menu *QA* with its own icon; Testing, Library, Configuration
4     Inheritance             ``models/project_task.py``,                  Task: run counter, verdict, requirements; user: open runs counter; views extended by xpath, no replace
                              ``models/res_users.py``
5     Wizard                  ``wizard/qa_retest_wizard.py``               Creates a new run from the failed cases; button on the run and Action menu
6     Report                  ``report/qa_test_run_templates.xml``         PDF per run with company header and footer, summary and line results
7     Demo                    ``demo/*.xml``                               3 users, 4 areas, 4 tags, 4 requirements, 6 cases, 5 runs in all states
8     Tests                   ``tests/test_qa_test_management.py``         14 tests: logic of every model, error texts, ``with_user`` access checks
9     Security                ``security/qa_security.xml``                 Tester and QA Lead with ``implied_ids``; ACL for both; rules: tester sees own runs and lines
10    Documentation           ``README.rst``,                              This file, docstrings, module page with images
                              ``static/description/index.html``
11    Translations            ``i18n/uk_UA.po``                            Ukrainian, exported by Odoo; source strings in English
12    Code quality            ``ruff.toml`` (repository root)              ruff check and format clean; install and uninstall without errors
13    Invariant               ``models/qa_test_run.py``                    Done run has results on all lines: state machine + constraint, see above
====  ======================  ===========================================  ======================================================================

Usage
=====

#. Install the module with demo data and log in as ``qa_tester``.
#. Open *QA > Testing > Test Runs* and open a draft run; click **Start**.
#. Set Pass or Fail on the lines; write a comment for each Fail; click **Done**.
#. On a failed run click **Retest Failed**; print the run with **Print**.
#. Open *QA > Testing > Test Results* and switch to the pivot or graph view.

Tests
=====

::

    python odoo-bin -c odoo.conf -d <db> -u qa_test_management \
        --test-enable --test-tags /qa_test_management --stop-after-init

Credits
=======

Author: Denys Vialov. License: LGPL-3.
