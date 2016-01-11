pair<int, int> smart_div(int a, int b) {
	if (a < 0) {
		if (b < 0) {
			return make_pair(a / b, a % b);
		} else {
			int x = a / b;
			if (a % b != 0) {
				x--;
			}
			return make_pair(x, abs(b) - abs(a % b));
		}
	} else {
		if (b < 0) {
			int x = a / b;
			if (a % b != 0) {
				x--;
			}
			return make_pair(x, -(abs(b) - abs(a % b)));
		} else {
			return make_pair(a / b, a % b);
		}
	}
}