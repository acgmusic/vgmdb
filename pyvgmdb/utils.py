from lxml import etree
from pyvgmdb.xpaths import main_xpaths_dict


class SafeEtree:
    def __init__(self, tree, dict_path=None):
        self.etree = tree
        self.dict_path = dict_path

    def xpath(self, key, final=True):
        xpath_dict = main_xpaths_dict
        if self.dict_path is not None:
            for p in self.dict_path:
                xpath_dict = xpath_dict[p]

        if key not in xpath_dict:
            raise Exception(f"key '{key}' is not found in dict path: {self.dict_path}"
                            f"please add xpath item in file: xpaths.py")
        xpath = xpath_dict[key]['xpath']
        res = self.etree.xpath(xpath)
        if not res:
            raise Exception(f"element named '{key}' is not found in current html page, "
                            f"maybe you can change its xpath in file: ./xpaths.py "
                            f"dict path is: {self.dict_path}")
        if final:
            return res
        else:
            new_dict_path = self.dict_path[:] if self.dict_path is not None else []
            new_dict_path.append(key)
            return self.__class__(res, new_dict_path)

    def __getitem__(self, item, final=False):
        return self.__class__(self.etree[item], self.dict_path)

    def __len__(self):
        return len(self.etree)

