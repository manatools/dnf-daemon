# -*- coding: utf-8 -*-

from apitest import TestBase
from dnfdaemon.client import LockedError
import time

"""
This module is used for testing new unit tests
When the test method is completted it is move som test-api.py

use 'nosetest -v -s unit-devel.py' to run the tests
"""


class TestAPIDevel(TestBase):

    def __init__(self, methodName='runTest'):
        TestBase.__init__(self, methodName)

    def test_Locking(self):
        '''
        System: Unlock and Lock
        '''
        print()
        # release the lock (grabbed by setUp)
        self.Unlock()
        # calling a method without a lock should raise a YumLockedError
        # self.assertRaises(YumLockedError,self.Install, '0xFFFF')
        # trying to unlock method without a lock should raise a YumLockedError
        self.assertRaises(LockedError, self.Unlock)
        # get the Lock again, else tearDown will fail
        self.Lock()

    def test_GetPackages(self):
        '''
        System: GetPackages
        '''
        print()
        for narrow in ['installed', 'available']:
            print(' Getting packages : %s' % narrow)
            pkgs = self.GetPackages(narrow)
            self.assertIsInstance(pkgs, list)
            self.assertGreater(len(pkgs), 0)  # the should be more than once
            print('  packages found : %s ' % len(pkgs))
            pkg_id = pkgs[-1]  # last pkg in list
            print(pkg_id)
            self._show_package(pkg_id)
        for narrow in ['updates', 'obsoletes', 'recent', 'extras']:
            print(
                '  ==================== Getting packages : %s =============================' %
                narrow)
            pkgs = self.GetPackages(narrow)
            self.assertIsInstance(pkgs, list)
            print('  packages found : %s ' % len(pkgs))
            if len(pkgs) > 0:
                pkg_id = pkgs[0]  # last pkg in list
                print(pkg_id)
                self._show_package(pkg_id)
        for narrow in ['notfound']:  # Dont exist, but it should not blow up
            print(' Getting packages : %s' % narrow)
            pkgs = self.GetPackages(narrow)
            self.assertIsInstance(pkgs, list)
            self.assertEqual(len(pkgs), 0)  # the should be notting
            print('  packages found : %s ' % len(pkgs))

    def test_AnyUpdate(self):
        '''
        System: GetPackages(update)
        '''
        print()
        # make sure there is one update
        self._remove_if_installed('foobar')  # make sure pkg is not installed
        rc, output = self.Install('foobar-1.0')
        if rc:
            self.show_transaction_result(output)
            self.RunTransaction()
        for narrow in ['updates']:
            print(
                '  ==================== Getting packages : %s =============================' %
                narrow)
            pkgs = self.GetPackages(narrow)
            self.assertIsInstance(pkgs, list)
            print('  packages found : %s ' % len(pkgs))
            self.assertGreater(len(pkgs), 0)
        self._remove_if_installed('foobar')  # make sure pkg is not installed

    def test_GetPackagesByName(self):
        '''
        System: GetPackagesByName
        '''
        print()
        print("Get all available versions of foo")
        pkgs = self.GetPackagesByName('foo', newest_only=False)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        num1 = len(pkgs)
        self.assertNotEqual(num1, 0)  # yum should always be there
        for pkg in pkgs:
            print("  Package : %s" % pkg)
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkg)
            self.assertEqual(n, "foo")
        print("Get newest versions of foo")
        pkgs = self.GetPackagesByName('foo', newest_only=True)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        num2 = len(pkgs)
        self.assertEqual(num2, 1)  # there can only be one :)
        for pkg in pkgs:
            print("  Package : %s" % pkg)
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkg)
            self.assertEqual(n, "foo")
        print("Get the newest packages starting with foo")
        pkgs = self.GetPackagesByName('foo*', newest_only=True)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        num3 = len(pkgs)
        self.assertGreater(num3, 1)  # there should be more than one :)
        for pkg in pkgs:
            print("  Package : %s" % pkg)
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkg)
            self.assertTrue(n.startswith('foo'))

    def test_GetPackagesByNameWithAttr(self):
        '''
        System: GetPackagesByName ( with attr)
        '''
        print()
        print("Get all available versions of foo")
        pkgs = self.GetPackagesByName(
            'foo',
            attr=['summary',
                  'size',
                  'action'],
            newest_only=False)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        num1 = len(pkgs)
        self.assertNotEqual(num1, 0)  # foo should always be there
        for pkg_id, summary, size, action in pkgs:
            self.assertIsInstance(summary, str)
            self.assertIsInstance(size, int)
            self.assertIsInstance(action, str)
            print(
                "  Package : %s Size : %i  Action : %s" %
                (pkg_id, size, action))
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkg_id)
            self.assertEqual(n, "foo")

    def test_Repositories(self):
        '''
        System: GetRepository and GetRepo
        '''
        print()
        print("  Getting enabled repos")
        repos = self.GetRepositories('')
        self.assertIsInstance(repos, list)
        for repo_id in repos:
            print("    Repo : %s" % repo_id)
        print("  Getting *-source repos")
        repos = self.GetRepositories('*-source')
        self.assertIsInstance(repos, list)
        for repo_id in repos:
            print("    Repo : %s" % repo_id)
            self.assertTrue(repo_id.endswith('-source'))
        print("  \nGetting fedora repository")
        repo = self.GetRepo('updates')
        self.assertIsInstance(repo, dict)
        print("  Repo: fedora")
        print("  Name : %s " % repo['name'])
        print("  Metalink :\n  %s " % repo['metalink'])
        print("  enabled : %s " % repo['enabled'])
        print("  gpgcheck : %s " % repo['gpgcheck'])

        # check for a repo not there
        repo = self.GetRepo('XYZCYZ')
        self.assertIsNone(repo)

    def test_Search(self):
        '''
        System: Search
        '''
        attrs = ['summary']
        fields = ['name', 'summary']
        keys = ['yum', 'plugin']
        pkgs = self.Search(fields, keys, attrs, True, True, False)
        self.assertIsInstance(pkgs, list)
        for elem in pkgs:
            print(type(elem))
            self.assertIsInstance(elem, list)
            (p, summary) = elem
            summary = self.GetAttribute(p, 'summary')
            print(str(p), summary)
            self.assertTrue(keys[0] in str(p) or keys[0] in summary)
            self.assertTrue(keys[1] in str(p) or keys[1] in summary)
        attrs = []
        keys = ['yum', 'zzzzddddsss']  # second key should not be found
        pkgs = self.Search(fields, keys, attrs, True, True, False)
        self.assertIsInstance(pkgs, list)
        print("found %i packages" % len(pkgs))
        self.assertEqual(len(pkgs), 0)  # when should not find any matches
        keys = ['yum', 'zzzzddddsss']  # second key should not be found
        pkgs = self.Search(fields, keys, attrs, False, True, False)
        self.assertIsInstance(pkgs, list)
        print("found %i packages" % len(pkgs))
        self.assertGreater(len(pkgs), 0)  # we should find some matches

    def test_PackageActions(self):
        """
        System: GetPackageWithAttributes & GetAttribute (action)
        """
        print()
        flt_dict = {'installed': ['remove'], 'updates': ['update'], 'obsoletes': [
            'obsolete'], 'available': ['install', 'remove', 'update', 'obsolete']}
        for flt in flt_dict.keys():
            now = time.time()
            result = self.GetPackages(flt, ['summary', 'size'])
            print(
                "%s, # = %s, time = %.3f" %
                (flt, len(result), time.time() - now))
            self.assertIsInstance(result, list)  # result is a list
            i = 0
            for elem in result:
                self.assertIsInstance(elem, list)  # each elem is a list
                self.assertEqual(len(elem), 3)  # 3 elements
                i += 1
                if i > 10:
                    break  # only test the first 10 elements
                now = time.time()
                action = self.GetAttribute(elem[0], 'action')
                name = elem[0].split(",")[0]
                print(
                    "    %s = %s , time = %.3f" %
                    (name, action, time.time() - now))
                self.assertIn(action, flt_dict[flt])

    def test_Groups(self):
        """
        System: Groups (GetGroups & GetGroupPackages)
        """
        print()
        self._enable_default_repos()
        result = self.GetGroups()
        i = 0
        for cat, grps in result:
            i += 1
            if i == 3:
                break
            # cat: [category_id, category_name, category_desc]
            self.assertIsInstance(cat, list)  # cat is a list
            self.assertIsInstance(grps, list)  # grps is a list
            self.assertEqual(len(cat), 3)  # cat has 3 elements
            print(" --> %s" % cat[0])
            j = 0
            for grp in grps:
                j += 1
                if j == 3:
                    break
                # [group_id, group_name, group_desc, group_is_installed]
                self.assertIsInstance(grp, list)  # grp is a list
                self.assertEqual(len(grp), 4)  # grp has 4 elements
                print(
                    "   tag: %s name: %s \n       desc: %s \n"
                    "       installed : %s " % tuple(grp))
                # Test GetGroupPackages
                grp_id = grp[0]
                pkgs = self.GetGroupPackages(grp_id, 'all', [])
                self.assertIsInstance(pkgs, list)  # cat is a list
                print("       # of Packages in group         : ", len(pkgs))
                pkgs = self.GetGroupPackages(grp_id, 'default', [])
                self.assertIsInstance(pkgs, list)  # cat is a list
                print("       # of Default Packages in group : ", len(pkgs))
                if len(pkgs) > 0:  # some packages has no default pkgs
                    elem = pkgs[0]  # pkg_id
                    self.assertIsInstance(elem, str)
                    pkgs = self.GetGroupPackages(
                        grp_id, 'default', ['size', 'summary'])
                    self.assertIsInstance(pkgs, list)  # cat is a list
                    elem = pkgs[0]  # [pkg_id, size, summary]
                    self.assertIsInstance(elem, list)
                    self.assertEqual(len(elem), 3)  # has 3 elements

    def test_Downgrades(self):
        '''
        System: GetAttribute( downgrades )
        '''
        print("Get newest versions of bar")
        pkgs = self.GetPackagesByName('bar', newest_only=True)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        num2 = len(pkgs)
        self.assertEqual(num2, 1)  # there can only be one :)
        downgrades = self.GetAttribute(pkgs[0], 'downgrades')
        self.assertIsInstance(downgrades, list)
        (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkgs[0])
        inst_evr = "%s:%s.%s" % (e, v, r)
        print("Installed : %s" % pkgs[0])
        for id in downgrades:
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(id)
            evr = "%s:%s.%s" % (e, v, r)
            self.assertTrue(evr < inst_evr)
            print("  Downgrade : %s" % id)

    def test_GetConfig(self):
        '''
        System: GetConfig
        '''
        all_conf = self.GetConfig('*')
        self.assertIsInstance(all_conf, dict)
        for key in all_conf:
            print("   %s = %s" % (key, all_conf[key]))
        fastestmirror = self.GetConfig('fastestmirror')
        print("fastestmirror : %s" % fastestmirror)
        self.assertIn(fastestmirror, [True, False])
        not_found = self.GetConfig('not_found')
        print("not_found : %s" % not_found)
        self.assertIsNone(not_found)

#
# System Only Tests
#

    def test_History(self):
        '''
        System: GetHistoryByDays, GetHistoryPackages
        '''
        HISTORY_STATES = [
            'Install', 'True-Install', 'Reinstall', 'Reinstalled', 'Update', 'Updated', 'Downgrade',
            'Downgraded', 'Obsoleting', 'Obsoleted', 'Erased', 'Erase', 'Dep-Install']

        result = self.GetHistoryByDays(0, 5)
        self.assertIsInstance(result, list)
        for tx_mbr in result:
            tid, dt = tx_mbr
            print("%-4i - %s" % (tid, dt))
            pkgs = self.GetHistoryPackages(tid)
            self.assertIsInstance(pkgs, list)
            for (id, state, is_installed) in pkgs:
                print(id, state, is_installed)
                self.assertIn(state, HISTORY_STATES)
                self.assertIn(is_installed, [True, False, None])

    def test_HistorySearch(self):
        '''
        System: HistorySearch
        '''
        print()
        result = self.HistorySearch(['dnf'])  # this should be found
        print("# found = ", len(result))
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result, list)
        for tx_mbr in result:
            tid, dt = tx_mbr
            print("%i - %s" % (tid, dt))
            pkgs = self.GetHistoryPackages(tid)
            self.assertIsInstance(pkgs, list)
            for (tid, state, is_installed) in pkgs:
                if 'dnf' in tid:
                    print("     ", tid, state, is_installed)
                    self.assertIsInstance(is_installed, bool)

        # this should not be found
        result = self.HistorySearch(['thiscannotbefound'])
        print("# found = ", len(result))
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_DepsolveErr(self):
        '''
        System: DepSolveErrors
        '''
        print()
        #rc, output = self.Install('foo-dep-error')
        rc, output = self.Install('foo-dep-error bar-dep-error')
        print('  Return Code : %i' % rc)
        self.assertEqual(rc, False)
        self.assertIsInstance(output, list)
        self.assertGreater(len(output), 0)
        for msg in output:
            print("  MSG : %s" % msg)

    def test_AnyObsoletes(self):
        '''
        System: GetPackages(obsoletes)
        Cheking obsoletes handling
        '''
        print()
        # make sure there is one update
        self._remove_if_installed('bar-new')  # make sure pkg is not installed
        self._remove_if_installed('bar-old')  # make sure pkg is not installed
        rc, output = self.Install('bar-old')
        if rc:
            self.show_transaction_result(output)
            self.RunTransaction()
        for narrow in ['obsoletes']:
            print(
                '==================== Getting packages : %s '
                '=============================' % narrow)
            pkgs = self.GetPackages(narrow)
            self.assertIsInstance(pkgs, list)
            print('  packages found : %s ' % len(pkgs))
            self.assertGreater(len(pkgs), 0)
            for pkg in pkgs:
                print("    pkg: ", str(pkg))
        rc, output = self.Update('bar-new')
        if rc:
            self.show_transaction_result(output)
            for action, pkg_info in output:
                for pkg_id, size, obs_list in pkg_info:
                    # The obs_list should be a list, with >0 elements
                    self.assertIsInstance(obs_list, list)
                    self.assertGreater(len(pkgs), 0)
        self._remove_if_installed('bar-old')  # make sure pkg is not installed

    def test_GetPackagesByNameForInstalledPkg(self):
        '''
        System: GetPackagesByName(bar is installed)
        if bar-2.0 is installed, the GetPackagesByName('bar', newest_only=False)
        should only list the installed bar-2.0 and the available bar-1.0
        and not the available bar-2.0
        '''
        print()
        # make sure there is one update
        self._remove_if_installed('bar')  # make sure pkg is not installed
        rc, output = self.Install('bar')
        self.assertTrue(rc)
        if rc:
            self.show_transaction_result(output)
            self.RunTransaction()
        pkgs = self.GetPackagesByName('bar', newest_only=False)
        print(pkgs)
        # pkgs should be a list instance
        self.assertIsInstance(pkgs, list)
        self.assertEqual(len(pkgs), 2)  # bar should only be there twice
        for pkg in pkgs:
            print("  Package : %s" % pkg)
            (n, e, v, r, a, repo_id) = self.to_pkg_tuple(pkg)
            self.assertEqual(n, "bar")

