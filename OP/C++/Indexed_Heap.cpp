template<class T>
class Heap {
private:
	vector<T> arr;
	unordered_map<T, int> index;
	int get_above(int x) {
		return (x - 1) / 2;
	}
	
	int get_below_first(int x)  {
		return (x * 2) + 1;
	}
	
public:
	Heap() {
		
	}
	
	Heap(vector<T> &arr) {
		this->arr = arr;
		heapify();
	}
	
	void up(int ind) {
		while (ind != 0 && arr[get_above(ind)] < arr[ind]) {
			index[arr[get_above(ind)]] = ind;
			tie(arr[ind], arr[get_above(ind)]) = make_tuple(arr[get_above(ind)], arr[ind]);
			ind = get_above(ind);
		}
		index[arr[ind]] = ind;
	}
	
	T pop() {
		T x = arr[0];
		tie(arr[0], arr.back()) = make_tuple(arr.back(), arr[0]);
		arr.pop_back();
		if (!arr.empty()) {
			down(0);
		}
		return x;
	}
	
	void down(int ind) {
		while (true) {
			int x = get_below_first(ind);
			if (x >= arr.size()) {
				break;
			}
			if (x + 1 < arr.size()) {
				if (arr[x + 1] > arr[x]) {
					x++;
				}
			}
			if (arr[x] > arr[ind]) {
				index[arr[x]] = ind;
				tie(arr[x], arr[ind]) = make_tuple(arr[ind], arr[x]);
				ind = x;
			} else {
				break;
			}
		}
		index[arr[ind]] = ind;
	}
	
	void heapify() {
		for (int i = arr.size() - 1; i > -1; i--) {
			up(i);
			down(i);
		}
	}
	
	int size() {
		return arr.size();
	}
};