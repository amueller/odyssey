"""
ImportAnalyzer.py
====================================
The module that defines ImportAnalyzer.

"""
import parso
import operator
from odyssey.utils import sklearn_meta_data
from odyssey.utils.parse import parso_parse


class ImportAnalyzer:
    """ImportAnalyzer analyzes how classes, submodules and functions are
    imported."""

    def __init__(self, package, accepted_list):
        """Initialize the ImportAnalyzer.

        Parameters
        ----------
        package: string
            Python package to be counted.

        accepted_list : string
            A list of tokens that will be extracted out and counted.

        Returns
        -------

        object
            returns an initialized ImportAnalyzer object.

        """
        from collections import defaultdict
        self.package = package
        self.accepted_list = self._get_default_accepted_list(accepted_list)
        self.counter = defaultdict(list)
        self.entry = None

    def parse(self, entry):
        """Parse a BigQueryGithubEntry for import analysis.

        Parameters
        ----------
        entry: BigQueryGithubEntry
            A BigQueryGithubEntry to be parsed

        """
        self.entry = entry
        node = parso_parse(entry.code)
        self._dfs(node)

    def get_common(self, n=None, _reverse=True):
        """Get common imported values.

        Parameters
        ----------
        n : int or None, optional (default=None)
            the top n most/least imported values to be returned. If set to
            None, all results will be returned.

        _reverse : bool, optional (default=True)
            if _reverse, returns value in descending order.

        Returns
        -------
        list
            return a list of tuples containing (value, count)

        """
        output = self._entry_list_to_count()
        if n is None:
            return sorted(output.items(), key=operator.itemgetter(1),
                          reverse=_reverse)
        return sorted(output.items(), key=operator.itemgetter(1),
                      reverse=_reverse)[:n]

    def get_source(self, s):
        """Get the source entries for a specific value

        Parameters
        ----------
        s : string
            Value to get source for. Should be in accepted_list.

        Returns
        -------
        list
            return a list of BigQueryGithubEntry.

        """
        return self.counter[s] if s in self.counter else []

    def get_most_common(self, n=None):
        """Get most common n imported values.

        Parameters
        ----------
        n : int or None, optional (default=None)
            the top n most imported values to be returned. If set to None, all
            results will be returned.

        Returns
        -------
        list
            return a list of tuples containing (value, count)

        """
        return self.get_common(n)

    def get_least_common(self, n=None):
        """Get least common n imported values.

        Parameters
        ----------
        n : int or None, optional (default=None)
            the top n least imported values to be returned. If set to None, all
            results will be returned.

        Returns
        -------
        list
            return a list of tuples containing (value, count)

        """
        return self.get_common(n, _reverse=False)

    def get_by_filter(self, f):
        """Get imported values, filtered by f.

        Parameters
        ----------
        f : function
            used as filter(f, get_most_common())

        Returns
        -------
        list
            return a list of tuples containing (value, count)

        """
        return filter(f, self.get_most_common())

    def _entry_list_to_count(self):
        return {k: len(v) for k, v in self.counter.items()}

    def _get_default_accepted_list(self, accepted_list):
        if type(accepted_list) is str:
            if accepted_list.upper() == "SKLEARN_ALL":
                return (sklearn_meta_data.get_all_functions()
                        + sklearn_meta_data.get_all_submodules()
                        + sklearn_meta_data.get_all_models())
            elif accepted_list.upper() == "SKLEARN_FUNCTION":
                return sklearn_meta_data.get_all_functions()
            elif accepted_list.upper() == "SKLEARN_SUBMODULE":
                return sklearn_meta_data.get_all_submodules()
            elif accepted_list.upper() == "SKLEARN_CLASS":
                return sklearn_meta_data.get_all_models()
            else:
                raise Exception("Do not understand %s! " % accepted_list
                                + "Default accepted list not supported!")
        else:
            return accepted_list

    def _dfs(self, node):
        if node.type == 'import_from':
            self._handle_import_from(node)
        elif node.type == 'import_name':
            self._handle_import_name(node)
        elif hasattr(node, 'children'):
            for child in node.children:
                self._dfs(child)
        else:
            pass

    def _count(self, value):
        if value in self.accepted_list:
            if (len(self.counter[value]) == 0
                    or self.counter[value][-1] != self.entry):
                # Count by file, so do not count the same value twice
                self.counter[value].append(self.entry)

    def _handle_import_from(self, node):
        def get_imports(node):
            if (isinstance(node.children[3], parso.python.tree.Operator)
                    and node.children[3].value == "("):
                return node.children[4]
            else:
                return node.children[3]
        module = node.children[1]
        imports = get_imports(node)
        if (module.type == 'dotted_name'
                and module.children[0].value == self.package):
            # Case 1: from Library.B import C
            for dotted_name in module.children:
                if dotted_name.type == 'name':
                    self._count(dotted_name.value)

        if ((module.type == 'name' and module.value == self.package)
                or (module.type == 'dotted_name'
                    and module.children[0].value == self.package)):
            if imports.type == "name":
                # Case 2: from Library import A
                self._count(imports.value)
            elif imports.type == "import_as_names":
                for child in imports.children:
                    if child.type == "name":
                        # Case 3: from Library import A, B
                        self._count(child.value)
                    elif child.type == "import_as_name":
                        # Case 4: from Library import A, B as C
                        if child.children[0].type == "name":
                            self._count(child.children[0].value)
            elif imports.type == "operator" and imports.value == "*":
                # Do not handle 'from Library import *' yet
                pass
            elif imports.type == "import_as_name":
                if imports.children[0].type == "name":
                    # Case 5: from Library import A as B
                    self._count(imports.children[0].value)
            else:
                raise Exception("Unexpected import line! %r" % node)

    def _handle_import_name(self, node):
        imports = node.children[1]
        if (imports.type == 'dotted_name'
                and imports.children[0].type == "name"
                and imports.children[0].value == self.package):
            # Case 6: import Library.A
            for child in imports.children[1:]:
                if child.type == "name":
                    self._count(child.value)
        elif (imports.type == 'dotted_as_name'
              and imports.children[0].type == "dotted_name"):
            # Case 7: import Library.A as B
            import_dot = imports.children[0]
            if (import_dot.children[0].type == "name"
                    and import_dot.children[0].value == self.package):
                for child in import_dot.children[1:]:
                    if child.type == "name":
                        self._count(child.value)
