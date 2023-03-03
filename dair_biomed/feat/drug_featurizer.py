import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

import rdkit.Chem as Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")
from sklearn.preprocessing import OneHotEncoder
from torch_geometric.data import Data
from transformers import BertTokenizer

from feat.base_featurizer import BaseFeaturizer
from feat.kg_featurizer import SUPPORTED_KG_FEATURIZER
from feat.text_featurizer import SUPPORTED_TEXT_FEATURIZER

def one_hot_encoding(x, allowable_set, encode_unknown=False):
    """One-hot encoding.
    """
    if encode_unknown and (allowable_set[-1] is not None):
        allowable_set.append(None)

    if encode_unknown and (x not in allowable_set):
        x = None

    return list(map(lambda s: x == s, allowable_set))

def safe_index(l, e):
    """
    Return index of element e in list l. If e is not present, return the last index
    """
    try:
        return l.index(e)
    except:
        return len(l) - 1

# Atom featurization: Borrowed from dgllife.utils.featurizers.py

def atom_type_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the type of an atom.
    """
    if allowable_set is None:
        allowable_set = ['C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'Mg', 'Na', 'Ca',
                         'Fe', 'As', 'Al', 'I', 'B', 'V', 'K', 'Tl', 'Yb', 'Sb', 'Sn',
                         'Ag', 'Pd', 'Co', 'Se', 'Ti', 'Zn', 'H', 'Li', 'Ge', 'Cu', 'Au',
                         'Ni', 'Cd', 'In', 'Mn', 'Zr', 'Cr', 'Pt', 'Hg', 'Pb']
    return one_hot_encoding(atom.GetSymbol(), allowable_set, encode_unknown)

def atom_degree_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the degree of an atom.
    """
    if allowable_set is None:
        allowable_set = list(range(11))
    return one_hot_encoding(atom.GetDegree(), allowable_set, encode_unknown)

def atom_implicit_valence_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the implicit valence of an atom.
    """
    if allowable_set is None:
        allowable_set = list(range(7))
    return one_hot_encoding(atom.GetImplicitValence(), allowable_set, encode_unknown)

def atom_formal_charge(atom):
    """Get formal charge for an atom.
    """
    return [atom.GetFormalCharge()]

def atom_num_radical_electrons(atom):
    return [atom.GetNumRadicalElectrons()]

def atom_hybridization_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the hybridization of an atom.
    """
    if allowable_set is None:
        allowable_set = [Chem.rdchem.HybridizationType.SP,
                         Chem.rdchem.HybridizationType.SP2,
                         Chem.rdchem.HybridizationType.SP3,
                         Chem.rdchem.HybridizationType.SP3D,
                         Chem.rdchem.HybridizationType.SP3D2]
    return one_hot_encoding(atom.GetHybridization(), allowable_set, encode_unknown)

def atom_is_aromatic(atom):
    """Get whether the atom is aromatic.
    """
    return [atom.GetIsAromatic()]

def atom_total_num_H_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the total number of Hs of an atom.
    """
    if allowable_set is None:
        allowable_set = list(range(5))
    return one_hot_encoding(atom.GetTotalNumHs(), allowable_set, encode_unknown)

def atom_is_in_ring(atom):
    """Get whether the atom is in ring.
    """
    return [atom.IsInRing()]

def atom_chirality_type_one_hot(atom, allowable_set=None, encode_unknown=False):
    """One hot encoding for the chirality type of an atom.
    """
    if not atom.HasProp('_CIPCode'):
        return [False, False]

    if allowable_set is None:
        allowable_set = ['R', 'S']
    return one_hot_encoding(atom.GetProp('_CIPCode'), allowable_set, encode_unknown)

# Atom featurization: Borrowed from dgllife.utils.featurizers.py

def bond_type_one_hot(bond, allowable_set=None, encode_unknown=False):
    """One hot encoding for the type of a bond.
    """
    if allowable_set is None:
        allowable_set = [Chem.rdchem.BondType.SINGLE,
                         Chem.rdchem.BondType.DOUBLE,
                         Chem.rdchem.BondType.TRIPLE,
                         Chem.rdchem.BondType.AROMATIC]
    return one_hot_encoding(bond.GetBondType(), allowable_set, encode_unknown)

class DrugOneHotFeaturizer(BaseFeaturizer):
    smiles_char = ['?', '#', '%', ')', '(', '+', '-', '.', '1', '0', '3', '2', '5', '4',
       '7', '6', '9', '8', '=', 'A', 'C', 'B', 'E', 'D', 'G', 'F', 'I',
       'H', 'K', 'M', 'L', 'O', 'N', 'P', 'S', 'R', 'U', 'T', 'W', 'V',
       'Y', '[', 'Z', ']', '_', 'a', 'c', 'b', 'e', 'd', 'g', 'f', 'i',
       'h', 'm', 'l', 'o', 'n', 's', 'r', 'u', 't', 'y']

    def __init__(self, max_len=256):
        super(DrugOneHotFeaturizer, self).__init__()
        self.max_len = max_len
        self.enc = OneHotEncoder().fit(np.array(self.smiles_char).reshape(-1, 1))

    def __call__(self, data):
        temp = [c if c in self.smiles_char else '?' for c in data]
        if len(temp) < self.max_len:
            temp = temp + ['?'] * (self.max_len - len(temp))
        else:
            temp = temp [:self.max_len]
        return self.enc.transform(np.array(temp).reshape(-1, 1)).toarray().T

class DrugBERTTokFeaturizer(BaseFeaturizer):
    def __init__(self, config):
        super(DrugBERTTokFeaturizer, self).__init__()
        self.max_length = config["max_length"]
        self.tokenizer = BertTokenizer.from_pretrained(config["model_name_or_path"])

    def __call__(self, data):
        result = self.tokenizer(data, max_length=self.max_length, padding='max_length', truncation=True, return_tensors='pt')
        return result.data

class DrugBPEFeaturizer(BaseFeaturizer):
    def __init__(self, config):
        super(DrugBPEFeaturizer, self).__init__()

        from subword_nmt.apply_bpe import BPE, read_vocabulary
        import codecs

        self.bpe = BPE(
            codecs.open(config["code_name"], encoding="utf8"), 
            vocab=read_vocabulary(codecs.open(config["vocabulary"], encoding="utf8"), config["vocabulary_threshold"]),
            separator="~~", 
        )
        self.vocabs = {}
        lines = open(config["vocabulary"], "r").readlines()
        for line in lines:
            wd = line.strip('\n').split(' ')
            self.vocabs[wd[0]] = len(self.vocabs)
        self.max_length = config["max_length"]

    def __call__(self, data):
        bpe_result = self.bpe.process_line(data).split(" ")
        result = [self.vocabs[x] if x in self.vocabs else len(self.vocabs) for x in bpe_result]
        if len(result) > self.max_length - 2:
            result = result[:self.max_length - 2]
        input_ids = torch.LongTensor([102] + [i + 30700 for i in result] + [103] + [0] * (self.max_length - 2 - len(result)))
        attn_mask = torch.LongTensor([1] * (len(result) + 2) + [0] * (self.max_length - len(result) - 2))
        token_type_ids = torch.zeros_like(attn_mask).long()
        return {
            "input_ids": input_ids,
            "attention_mask": attn_mask,
            "token_type_ids": token_type_ids
        }

class DrugTGSAFeaturizer(BaseFeaturizer):
    def __init__(self, config):
        super(DrugTGSAFeaturizer, self).__init__()
        self.config = config

    def atom_feature(self, atom):
        """
        Converts rdkit atom object to feature list of indices
        :param mol: rdkit atom object
        :return: list
        8 features are canonical, 2 features are from OGB
        """
        featurizer_funcs = [
            atom_type_one_hot,
            atom_degree_one_hot,
            atom_implicit_valence_one_hot,
            atom_formal_charge,
            atom_num_radical_electrons,
            atom_hybridization_one_hot,
            atom_is_aromatic,
            atom_total_num_H_one_hot,
            atom_is_in_ring,
            atom_chirality_type_one_hot,
        ]
        atom_feature = np.concatenate([func(atom) for func in featurizer_funcs], axis=0)
        return atom_feature

    def bond_feature(self, bond):
        """
        Converts rdkit bond object to feature list of indices
        :param mol: rdkit bond object
        :return: list
        """
        featurizer_funcs = [bond_type_one_hot]
        bond_feature = np.concatenate([func(bond) for func in featurizer_funcs], axis=0)

        return bond_feature
    
    def __call__(self, data):
        mol = Chem.MolFromSmiles(data)
        """
        Converts SMILES string to graph Data object without remove salt
        :input: SMILES string (str)
        :return: pyg Data object
        """
        # atoms
        atom_features_list = []
        for atom in mol.GetAtoms():
            atom_features_list.append(self.atom_feature(atom))
        x = np.array(atom_features_list, dtype=np.int64)

        # bonds
        num_bond_features = 3  # bond type, bond stereo, is_conjugated
        if len(mol.GetBonds()) > 0:  # mol has bonds
            edges_list = []
            edge_features_list = []
            for bond in mol.GetBonds():
                i = bond.GetBeginAtomIdx()
                j = bond.GetEndAtomIdx()
                edge_feature = self.bond_feature(bond)
                # add edges in both directions
                edges_list.append((i, j))
                edge_features_list.append(edge_feature)
                edges_list.append((j, i))
                edge_features_list.append(edge_feature)

            edge_index = np.array(edges_list, dtype=np.int64).T
            edge_attr = np.array(edge_features_list, dtype=np.int64)

        else:  # mol has no bonds
            edge_index = np.empty((2, 0), dtype=np.int64)
            edge_attr = np.empty((0, num_bond_features), dtype=np.int64)

        graph = Data(
            x=torch.tensor(x, dtype=torch.float),
            edge_index=torch.tensor(edge_index, dtype=torch.long),
            edge_attr=torch.tensor(edge_attr, dtype=torch.float),
        )
        return graph

class DrugGraphFeaturizer(BaseFeaturizer):
    allowable_features = {
        'possible_atomic_num_list':       list(range(1, 119)) + ['misc'],
        'possible_formal_charge_list':    [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 'misc'],
        'possible_chirality_list':        [
            Chem.rdchem.ChiralType.CHI_UNSPECIFIED,
            Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CW,
            Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CCW,
            Chem.rdchem.ChiralType.CHI_OTHER
        ],
        'possible_hybridization_list':    [
            Chem.rdchem.HybridizationType.SP,
            Chem.rdchem.HybridizationType.SP2,
            Chem.rdchem.HybridizationType.SP3,
            Chem.rdchem.HybridizationType.SP3D,
            Chem.rdchem.HybridizationType.SP3D2,
            Chem.rdchem.HybridizationType.UNSPECIFIED,
            'misc'
        ],
        'possible_numH_list':             [0, 1, 2, 3, 4, 5, 6, 7, 8, 'misc'],
        'possible_implicit_valence_list': [0, 1, 2, 3, 4, 5, 6],
        'possible_degree_list':           [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'misc'],
        'possible_number_radical_e_list': [0, 1, 2, 3, 4, 'misc'],
        'possible_is_aromatic_list':      [False, True],
        'possible_is_in_ring_list':       [False, True],
        'possible_bond_type_list':                 [
            Chem.rdchem.BondType.SINGLE,
            Chem.rdchem.BondType.DOUBLE,
            Chem.rdchem.BondType.TRIPLE,
            Chem.rdchem.BondType.AROMATIC,
            'misc'
        ],
        'possible_bond_dirs':             [  # only for double bond stereo information
            Chem.rdchem.BondDir.NONE,
            Chem.rdchem.BondDir.ENDUPRIGHT,
            Chem.rdchem.BondDir.ENDDOWNRIGHT
        ],
        'possible_bond_stereo_list':      [
            Chem.rdchem.BondStereo.STEREONONE,
            Chem.rdchem.BondStereo.STEREOZ,
            Chem.rdchem.BondStereo.STEREOE,
            Chem.rdchem.BondStereo.STEREOCIS,
            Chem.rdchem.BondStereo.STEREOTRANS,
            Chem.rdchem.BondStereo.STEREOANY,
        ], 
        'possible_is_conjugated_list': [False, True]
    }

    def __init__(self, config):
        super(DrugGraphFeaturizer, self).__init__()
        self.config = config

    def __call__(self, data):
        mol = Chem.MolFromSmiles(data)
        # atoms
        atom_features_list = []
        for atom in mol.GetAtoms():
            if self.config["name"] == "ogb":
                atom_feature = [
                    safe_index(self.allowable_features['possible_atomic_num_list'], atom.GetAtomicNum()),
                    self.allowable_features['possible_chirality_list'].index(atom.GetChiralTag()),
                    safe_index(self.allowable_features['possible_degree_list'], atom.GetTotalDegree()),
                    safe_index(self.allowable_features['possible_formal_charge_list'], atom.GetFormalCharge()),
                    safe_index(self.allowable_features['possible_numH_list'], atom.GetTotalNumHs()),
                    safe_index(self.allowable_features['possible_number_radical_e_list'], atom.GetNumRadicalElectrons()),
                    safe_index(self.allowable_features['possible_hybridization_list'], atom.GetHybridization()),
                    self.allowable_features['possible_is_aromatic_list'].index(atom.GetIsAromatic()),
                    self.allowable_features['possible_is_in_ring_list'].index(atom.IsInRing()),
                ]
            else:
                atom_feature = [
                    safe_index(self.allowable_features['possible_atomic_num_list'], atom.GetAtomicNum()),
                    self.allowable_features['possible_chirality_list'].index(atom.GetChiralTag())
                ]
            atom_features_list.append(atom_feature)
        x = torch.tensor(np.array(atom_features_list), dtype=torch.long)

        # bonds
        if len(mol.GetBonds()) <= 0:  # mol has no bonds
            num_bond_features = 3 if self.config["name"] == "ogb" else 2
            edge_index = torch.empty((2, 0), dtype=torch.long)
            edge_attr = torch.empty((0, num_bond_features), dtype=torch.long)
        else:  # mol has bonds
            edges_list = []
            edge_features_list = []
            for bond in mol.GetBonds():
                i = bond.GetBeginAtomIdx()
                j = bond.GetEndAtomIdx()
                if self.config["name"] == "ogb":
                    edge_feature = [
                        safe_index(self.allowable_features['possible_bond_type_list'], bond.GetBondType()),
                        self.allowable_features['possible_bond_stereo_list'].index(bond.GetStereo()),
                        self.allowable_features['possible_is_conjugated_list'].index(bond.GetIsConjugated()),
                    ]
                else:
                    edge_feature = [
                        self.allowable_features['possible_bond_type_list'].index(bond.GetBondType()),
                        self.allowable_features['possible_bond_dirs'].index(bond.GetBondDir())
                    ]
                edges_list.append((i, j))
                edge_features_list.append(edge_feature)
                edges_list.append((j, i))
                edge_features_list.append(edge_feature)

            # data.edge_index: Graph connectivity in COO format with shape [2, num_edges]
            edge_index = torch.tensor(np.array(edges_list).T, dtype=torch.long)

            # data.edge_attr: Edge feature matrix with shape [num_edges, num_edge_features]
            edge_attr = torch.tensor(np.array(edge_features_list), dtype=torch.long)

        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

        return data
    
class DrugMultiModalFeaturizer(BaseFeaturizer):
    def __init__(self, config):
        super(DrugMultiModalFeaturizer, self).__init__()
        self.modality = config["modality"]
        self.featurizers = {}
        if "structure" in config["modality"]:
            conf = config["featurizer"]["structure"]
            self.featurizers["structure"] = SUPPORTED_DRUG_FEATURIZER[conf["name"]](conf)
        if "KG" in config["modality"]:
            conf = config["featurizer"]["KG"]
            self.featurizers["KG"] = SUPPORTED_KG_FEATURIZER[conf["name"]](conf)
        if "text" in config["modality"]:
            conf = config["featurizer"]["text"]
            self.featurizers["text"] = SUPPORTED_TEXT_FEATURIZER[conf["name"]](conf)

    def set_drug2kgid_dict(self, drug2kgid):
        self.featurizers["KG"].set_transform(drug2kgid)

    def set_drug2text_dict(self, drug2text):
        self.featurizers["text"].set_transform(drug2text)

    def __call__(self, data):
        feat = {}
        for modality in self.modality:
            feat[modality] = self.featurizers[modality](data)
        return feat

SUPPORTED_DRUG_FEATURIZER = {
    "OneHot": DrugOneHotFeaturizer,
    "KV-PLM*": DrugBPEFeaturizer,
    "bert": DrugBERTTokFeaturizer,
    #"molclr": DrugMolCLRFeaturizer,
    "TGSA": DrugTGSAFeaturizer,
    "ogb": DrugGraphFeaturizer,
    "BaseGNN": DrugGraphFeaturizer,
    "MultiModal": DrugMultiModalFeaturizer,
}

if __name__ == "__main__":
    smi = "CCC=O"
    data = DrugGraphFeaturizer({"name": "ogb"})(smi)
    print(data.x, data.edge_index, data.edge_attr)

    smi = "[Cl].CCCNCCOCOC=CC=CC=CC=CC=C"
    data = DrugBPEFeaturizer({
        "name": "KV-PLM*",
        "code_name": "../assets/KV-PLM*/bpe_coding.txt",
        "vocabulary": "../assets/KV-PLM*/bpe_vocab.txt",
        "vocabulary_threshold": 80,
        "max_length": 32
    })(smi)
    print(data)