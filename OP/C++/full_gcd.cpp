tuple<int, int, int> full_gcd(int a, int b) {
	if (a == 0) {
		return mt(b, 0, 1);
	} else {
		auto t = full_gcd(b % a, a);
		int x1 = get<1>(t);
		int y1 = get<2>(t);
		return mt(get<0>(t), y1 - ((b / a) * x1), x1);
	}
}