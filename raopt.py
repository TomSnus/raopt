import sqlparse
import radb.ast
from radb.ast import *


parts = []
def rule_break_up_selections(ra):
    split_recursive(ra)
    parts.append(ra)
    parts_set = set(parts)
    parts_list = list(parts)
    select = None
    conditions = []
    sub_select = None
    from_part = None
    from_part_rename = None
    valExpr = [x for x in parts_list if isinstance(x, ValExprBinaryOp)]
    select = [x for x in parts_list if isinstance(x, Select)]
    project = [x for x in parts_list if isinstance(x, Project)]
    rel = extract_cross([x for x in parts_list if isinstance(x, RelExpr)], valExpr[1])
    val_rel = select[0].inputs[0]
    select = Select(valExpr[0], rel)
    print(select)
    if len(project) > 0:
        project[0].inputs[0]=select
        return project[0]
    return select

def split_recursive(ra):
    if ra is not None:
        for input in ra.inputs:
            if isinstance(input, Select):
                parts.append(input)
                split_recursive(input.cond)
            elif isinstance(ra, Select):
                parts.append(input)
                split_recursive(ra.cond)
            parts.append(input)
            split_recursive(input)

def extract_subSelect(select):
    sub = []
    for item in select.cond.inputs:
        sub.append(item)
    return sub


def extract_cross(rel, valExpr):
    relation = None
    if any(isinstance(x, Cross) for x in rel):
        relation = [elm for elm in rel if isinstance(elm, Cross)]
        relation[0].inputs[0].cond = valExpr
    elif any(isinstance(x, Rename) for x in rel):
        relation = [elm for elm in rel if isinstance(elm, Rename)]
        relation[0] = Select(valExpr, relation[0])
    else:
        relation = [elm for elm in rel if isinstance(elm, RelRef)]
        relation[0] = Select(valExpr, relation[0])
    return relation[0]
