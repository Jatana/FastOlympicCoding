#include <iostream>
#include <vector>
using namespace std;
typedef int tre;


vector<int> v;
void getErr2() {
	v[100] = 100;
}

void getErr() {
	__gcd(0, 0);
}

int main() {
	string x;
	cin >> x;
	cout << "pointer" << x;
	for (int i = 0; i < 1000000; i++) {
		cout << "";
	}

	// getErr();
	return 0;
}

