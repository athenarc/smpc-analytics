def preprocess(tree):
    fix_point = False
    while not fix_point:
        new_tree = preprocess_tree(tree)
        if new_tree == tree:
            fix_point = True
        tree = new_tree
    return tree

def preprocess_tree(tree):
    if not isinstance(tree,dict):
        return tree

    tree = {node: preprocess_tree(subtree) for node, subtree in tree.items()}
    allSubtrees = [str(subtree) for node, subtree in tree.items()]
    if allEqual(allSubtrees):
        subtree = allSubtrees[0]
        return subtree
    return tree

def allEqual(iterator):
    return len(set(iterator)) <= 1

if __name__ == '__main__':
    main()