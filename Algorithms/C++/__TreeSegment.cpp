namespace TreeSegment {
	typedef int value_type;
	typedef struct {int plus_mod;} Mod;
	
	value_type magic(const value_type &a, const value_type &b) {
		return a + b;
	}

	Mod merge_mods(const Mod &a, const Mod &b) {
		Mod mod;
		mod.plus_mod = a.plus_mod + b.plus_mod;
		return mod;
	}

	value_type apply_mod(int left, int right, const value_type &value, const Mod &mod) {
		return value + (mod.plus_mod * (right - left));
	}



	class Node {
	public:
		value_type value;
		Node *left_child = NULL, *right_child = NULL;
		bool pushed = true;

		Mod mod;

		int ths_left, ths_right;

		int length() { return ths_right - ths_left; };

		bool intersect(int left, int right) {
			return !(ths_right <= left || right <= ths_left);
		}

		bool is_list() {
			return (!left_child) && (!right_child);
		}

		void push() {
			//TODO!
			if (pushed) return;

			if (is_list()) {
				value = apply_mod(ths_left, ths_right, value, mod);
				pushed = true;
				return;
			}

			if (left_child) {
				if (left_child->pushed) {
					left_child->mod = mod;
				} else {
					left_child->mod = merge_mods(left_child->mod, mod);
				}
				left_child->pushed = false;
			}

			if (right_child) {
				if (right_child->pushed) {
					right_child->mod = mod;
				} else {
					right_child->mod = merge_mods(right_child->mod, mod);
				}
				right_child->pushed = false;
			}

			pushed = true;
			recalc();
		}

		void recalc() {
			// assert(mod.plus_mod == 0);
			if (is_list()) {
				assert(pushed);
				return;
			}
			assert(left_child && right_child);

			value_type vleft;
			if (left_child->pushed) {
				vleft = left_child->value;
			} else {
				vleft = apply_mod(left_child->ths_left, left_child->ths_right, left_child->value, left_child->mod);
			}

			value_type vright;
			if (right_child->pushed) {
				vright = right_child->value;
			} else {
				vright = apply_mod(right_child->ths_left, right_child->ths_right, right_child->value, right_child->mod);
			}

			value = magic(vleft, vright);
		}

		Node() {}
		
		Node(int left, int right, const vector<value_type> &arr) {
			ths_left = left;
			ths_right = right;
			if (left == right - 1) {
				value = arr[left];
			} else {
				int mid = (right + left) / 2;

				left_child = new Node(left, mid, arr);
				right_child = new Node(mid, right, arr);
			}
			recalc();
		}

		value_type query(int qleft, int qright) {
			assert(this);
			assert(!(ths_right <= qleft || qright <= ths_left));
			push();
			// if full include
			if (qleft <= ths_left && ths_right <= qright) {
				return value;
			}

			if (left_child && left_child->intersect(qleft, qright)) {
				if (right_child && right_child->intersect(qleft, qright)) {
					return magic(left_child->query(qleft, qright)
								, right_child->query(qleft, qright));
				} else {
					return left_child->query(qleft, qright);
				}
			} else {
				return right_child->query(qleft, qright);
			}
		}

		void replace(int ind, value_type d) {
			assert(this);
			push();
			// if full include
			if (is_list() && ths_left <= ind && ind < ths_right) {
				value = d;
				return;
			}

			if (left_child && left_child->intersect(ind, ind + 1)) {
				left_child->replace(ind, d);
			}
			
			if (right_child && right_child->intersect(ind, ind + 1)) {
				right_child->replace(ind, d);
			}
			recalc();
		}

		void update(int qleft, int qright, Mod pmod) {
			assert(this);
			assert(!(ths_right <= qleft || qright <= ths_left));
			push();
			// if full include
			if (qleft <= ths_left && ths_right <= qright) {
				if (pushed) {
					mod = pmod;
				} else {
					mod = merge_mods(mod, pmod);
				}
				pushed = false;
				push();
			} else {
				if (left_child && left_child->intersect(qleft, qright)) {
					left_child->update(qleft, qright, pmod);
				}

				if (right_child && right_child->intersect(qleft, qright)) {
					right_child->update(qleft, qright, pmod);
				}
			}
			recalc();
		}
	};
};
