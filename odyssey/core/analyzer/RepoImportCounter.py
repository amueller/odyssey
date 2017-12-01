"""
RepoImportCounter.py
====================================
The module that defines RepoImportCounter.

"""
from ..bigquery.BigQueryGithubEntry import BigQueryGithubEntry
import parso

class RepoImportCounter:
    """RepoImportCounter counts how many times other repos import the analyzed package."""
    def __init__(self, package):
        """Initialize the RepoImportCounter.
        
        Parameters
        ----------
        package: string
            Python package to be counted
        
        Returns
        -------

        object
            returns an initialized RepoImportCounter object.

        """
        from collections import Counter
        self.package = package
        self.counter = Counter()
        self.entry = None
        self.hasImport = False
    
    def parse(self, entry):
        """Parse a BigQueryGithubEntry for repo import count.
        
        Parameters
        ----------
        entry: BigQueryGithubEntry
            A BigQueryGithubEntry to be parsed

        """
        if not isinstance(entry, BigQueryGithubEntry):
            print("Cannot parse non-BigQueryGithubEntry!")
        self.entry = entry
        node = parso.parse(entry.code)
        self._dfs(node)
        if self.hasImport:
            self.counter.update([entry.repo_name])

    def get_most_common(self, n=None):
        """Get most common n repos.
        
        Parameters
        ----------
        n : int or None, optional (default=None)
            the name of top n repo that imports the package. If set to None, all results will be returned.

        Returns
        -------
        list
            list of tuple containing package name and count.

        """
        if n is None:
            return self.counter.most_common(len(self.counter))
        return self.counter.most_common(n)
    
    def _dfs(self, node):
        if self.hasImport:
            return
        if node.type == 'import_from':
            self._handleImportFrom(node)
        elif node.type == 'import_name':
            self._handleImportName(node)
        elif hasattr(node, 'children'):
            for child in node.children:
                self._dfs(child)
        else:
            pass

    def _count(self, value):
        # set hasImport to true so we can break from dfs earlier.
        self.hasImport = True

    def _handleImportFrom(self, node):
        def getImports(node):
            if isinstance(node.children[3], parso.python.tree.Operator) and node.children[3].value == "(":
                return node.children[4]
            else:
                return node.children[3]
        if self.hasImport:
            return
        module = node.children[1]
        imports = getImports(node)
        if module.type == 'dotted_name' and module.children[0].value == self.package:
            # Case 1: from Library.B import C
            for dotted_name in module.children:
                if dotted_name.type == 'name':
                    self._count(dotted_name.value)

        if ((module.type == 'name' and module.value == self.package) or
            (module.type == 'dotted_name' and module.children[0].value == self.package)):
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
    
    def _handleImportName(self, node):
        if self.hasImport:
            return
        imports = node.children[1]
        if imports.type == 'dotted_name' and imports.children[0] == self.package:
            # Case 6: import Library.A
            for child in imports.children[1:]:
                if child.type == "name":
                    self._count(child.value)
        elif imports.type == 'dotted_as_name' and imports.children[0] == self.package:
            # Case 7: import Library.A as B
            for child in imports.children[1:]:
                if child.type == "name":
                    self._count(child.value)