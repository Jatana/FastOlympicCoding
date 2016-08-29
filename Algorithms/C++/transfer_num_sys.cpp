#include <string>


int transfer_num_sys(int n, int from_ss, int to_ss) {
	// def to_10(n, p):
	int rez = 0;
	string s = to_string(n);
	for (auto c : s) {
		int x = c - '0';
		rez = (rez * from_ss) + x;
	}

	n = rez;
	vector<int> num;
	while (n >= to_ss) {
		num.push_back(n % to_ss);
		n /= to_ss;
	}
	num.push_back(n);
	reverse(num.begin(), num.end());
	rez = 0;
	for (auto x: num) {
		rez *= 10;
		rez += x;
		
	}
	return rez;
}