ull mul(ull a, ull b, ull m){
	if(b == 1) {
		return a;
	}
	if(b % 2 == 0){
		ull t = mul(a, b / 2, m);
		return (2 * t) % m;
	}
	return (mul(a, b - 1, m) + a) % m;
}

ull fast_pow(ull a, ull b, ull m){
	if(b == 0) {
		return 1;
	}
	if(b % 2 == 0){
		ull t = fast_pow(a, b / 2, m);
		return mul(t, t, m) % m;
	}
	return (mul(fast_pow(a, b - 1, m), a, m)) % m;
}