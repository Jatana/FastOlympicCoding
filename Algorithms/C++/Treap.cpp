class Node {
public:
	int value, prior, dupl_count;
	int value_sum, size;
	Node *less = NULL, *greater = NULL;

	Node() {}
	Node(int _value, int _prior) {
		value = _value;
		prior = _prior;
		dupl_count = 1;
		size = 1;
		value_sum = value;
	}


};

typedef Node* node_ptr;


class Treap {
public:

	int get_tree_size(node_ptr tree) {
		if (tree) {
			return tree->size;
		}
		return 0;
	}

	int get_value_sum(node_ptr tree) {
		if (tree) {
			return tree->value_sum;
		}
		return 0;
	}


	void update_tree_size(node_ptr &node) {
		node->size = node->dupl_count;
		if (node->less) {
			node->size += node->less->size; 
		}
		if (node->greater) {
			node->size += node->greater->size;
		}
	}


	void update_value_sum(node_ptr &node) {
		node->value_sum = node->value * node->dupl_count;
		if (node->less) {
			node->value_sum += node->less->value_sum; 
		}
		if (node->greater) {
			node->value_sum += node->greater->value_sum;
		}
	}

	void update_meta(node_ptr &node) {
		if (!node) return;
		update_tree_size(node);
		update_value_sum(node);
	}


	void __split(node_ptr tree, int value, node_ptr &less, node_ptr &greater) {
		if (!tree) {
			less = NULL;
			greater = NULL;
		} else if (tree->value > value) {
			__split(tree->less, value, less, tree->less);
			greater = tree;
		} else {
			__split(tree->greater, value, tree->greater, greater);
			less = tree;
		}
		update_meta(tree);
	}


	void __insert(node_ptr &tree, node_ptr item) {
		if (!tree) {
			tree = item;
		} else if (tree->value == item->value) {
			tree->dupl_count++;
		} else if (item->prior > tree->prior) {
			__split(tree, item->value, item->less, item->greater);
			tree = item;
		} else {
			if (item->value < tree->value) {
				__insert(tree->less, item);
			} else {
				__insert(tree->greater, item);
			}
		}
		update_meta(tree);
	}

	void merge(node_ptr &tree, node_ptr &less, node_ptr &greater) {
		if (!less || !greater) {
			if (less) {
				tree = less;
			} else {
				tree = greater;
			}
		} else if (less->prior > greater->prior) {
			merge(less->greater, less->greater, greater);
			tree = less;
		} else {
			merge(greater->less, less, greater->less);
			tree = greater;
		}
		update_meta(tree);
	}

	void __erase(node_ptr &tree, int value) {
		if (!tree) make_tl();
		if (tree->value == value) {
			tree->dupl_count--;
			if (tree->dupl_count == 0) {
				merge(tree, tree->less, tree->greater);
			}
		} else if (value > tree->value) {
			__erase(tree->greater, value);
		} else {
			__erase(tree->less, value);
		}
		update_meta(tree);
	}

	node_ptr root = NULL;

	Treap() {}


	void insert(int value) {
		__insert(root, new Node(value, rand()));
	}

	void erase(int value) {
		__erase(root, value);
	}

	int query(node_ptr tree, int max_size) {
		if (!tree) return 0;
		max_size = min(max_size, get_tree_size(tree));
		if (tree->size == max_size) {
			return tree->value_sum;
		}

		int r = query(tree->greater, max_size);
		max_size -= get_tree_size(tree->greater);
		if (max_size <= 0) {
			return r;
		}
		r += min(tree->dupl_count, max_size) * tree->value;
		max_size -= min(tree->dupl_count, max_size);
		if (max_size <= 0) {
			return r;
		}
		r += query(tree->less, max_size);
		return r;
	}

	void query_get_rez(node_ptr tree, int max_size, vector<int> &rez) {
		if (!tree) return;
		query_get_rez(tree->greater, max_size, rez);
	}

	void print_tree(node_ptr tree) {
		if (!tree) {
			return;
		}
		printf("{%lld, %lld, %lld} ", tree->value, tree->dupl_count, tree->size);
		// cout << tree->value << " ";
		printf("less->");
		print_tree(tree->less);
		printf("\n");
		printf("greater->");
		print_tree(tree->greater);
	}
};