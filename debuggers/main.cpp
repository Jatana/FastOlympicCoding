#include <iostream>
#include <string>
#include <vector>

using namespace std;


struct Point {
	int x, y;
	string very_long_string = "213_123_123_123";
};


void make_err() {
	vector<Point> v(6);
	string s = "HELLO";
	s += "123";
	cout << s << endl;
	// cout << x;
	// v.at(20);
}

int main() {
	make_err();
	string s;
	cin >> s;
	cout << "hello! " << s << endl;
	cin >> s;
	cout << "Kek!" << " " << s;

	// return 798;
}