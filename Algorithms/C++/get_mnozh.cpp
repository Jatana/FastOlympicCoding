vector<int> get_mnozh(int n) {
	vector<int> rez;
	int i = 2;
	while (n != 1 && i <= sqrt(n)) {
		while (n % i == 0) {
			rez.push_back(i);
			n /= i;
		}
		i++;
	}
	if (n != 1) {
		rez.push_back(n);
	}
	return rez;
}