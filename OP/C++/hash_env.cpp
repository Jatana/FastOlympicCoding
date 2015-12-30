ll MOD = 1000000000 + 7;
ll MOD2 = 1000000 + 7;
ll max_p = 31;


vector<ll> power(250);

ll get_substr_hash(vector<ll> &h, int i, int j) {
	ll hash = h[j];
	if (i > 0) {
		hash -= (h[i - 1] * power[j - i + 1]) % MOD;
	}
	return hash;
}


bool is_equal(vector<ll> &h1, vector<ll> &h2, int i, int j, int len) {
	int l1 = i, r1 = i + len - 1, l2 = j, r2 = j + len - 1;
	ll hash1 = h1[r1];
	if (l1 > 0) {
		hash1 -= (h1[l1 - 1] * power[r1 - l1 + 1]) % MOD;
	}
	ll hash2 = h2[r2];
	if (l2 > 0) {
		hash2 -= (h2[l2 - 1] * power[r2 - l2 + 1]) % MOD;
	}
	if (hash1 < 0) {
		hash1 = MOD - (abs(hash1) % MOD);
	}
	if (hash2 < 0) {
		hash2 = MOD - (abs(hash2) % MOD);
	}
	hash1 %= MOD;
	hash2 %= MOD;
	return hash1 == hash2;
}

int get_number(char c) {
	return c - 'a' + 1;
}


vector<ll> get_hash(string &s) {
	int n = s.length();
	vector<ll> hash(n);
	hash[0] = get_number(s[0]);
	for (int i = 1; i < n; i++) {
		hash[i] = ((hash[i - 1] * max_p) % MOD) + get_number(s[i]);
		hash[i] %= MOD;
	}
	return hash;
}