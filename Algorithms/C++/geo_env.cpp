
class point {
public:
	double x, y;

	point() {}
	
	point(double x, double y): x(x), y(y) {

	}
	double angle() {
		return atan2(y, x);
	}

	double length() {
		return sqrt((x * x) + (y * y));
	}

	friend istream& operator>>(istream &is, point &p) {
		is >> p.x >> p.y;
		return is;
	}

	friend ostream& operator<<(ostream &os, point &p) {
		os << p.x << p.y;
		return os;
	}

	point operator-(point &p) {
		return point(x - p.x, y - p.y);
	}

	bool operator==(point &p) {
		return this->x == p.x && this->y == p.y;
	}
};


class segment {
public:
	point p1, p2;

	segment() {
	}


	segment(point p1, point p2):p1(p1), p2(p2) {
	}


	friend istream &operator>>(istream &is, segment &s) {
		cin >> s.p1 >> s.p2;
		return is;
	}
};

class line {
public:
	point p1, p2;
	double a, b, c;
	
	void set_abc() {
		point p3 = (p1 - p2);
		// cout << p3 << nl;
		double q = p3.x;
		double p = p3.y;
		b = -q;
		a = p;
		c = -p * p2.x + q * p2.y;
	}

	line() {}
	line(point p1, point p2):p1(p1), p2(p2) {
		set_abc();
	}
	
	line(segment s) {
		p1 = s.p1;
		p2 = s.p2;
		set_abc();
	}
	
	line(double a, double b, double c):a(a), b(b), c(c) {
	}

	friend istream &operator>>(istream &is, line &l) {
		is >> l.p1 >> l.p2;
		l.set_abc();
		return is;
	}
};



namespace geo {
	bool is_equal(double x, double y, double precission) {
		return abs(x - y) < precission;
	}

	bool is_parralel(line l1, line l2) {
		if (l1.p1 == l1.p2 || l2.p1 == l2.p2) {
			return true;
		}

		if (l1.a == 0) {
			return l2.a == 0;
		} elif(l1.b == 0) {
			return l2.b == 0;
		} elif(l2.a == 0) {
			return l1.a == 0;
		} elif(l2.b == 0) {
			return l1.b == 0;
		} else {
			return is_equal((l1.a / l1.b), (l2.a / l2.b), 0.000001);
		}
	}

	point get_inter(line a, line b) {
		assert(a.a / a.b != b.a / b.b);
		double x = (b.c * a.b - a.c * b.b) / (a.a * b.b - b.a * a.b);
		double y = (b.c * a.a - a.c * b.a) / (b.a * a.b - a.a * b.b);
		return point(x, y);
	}

	bool is_inter(segment a, segment b) {
		line l1(a);
		line l2(b);
		if (is_parralel(l1, l2)) {
			// assert(l2.b != 0);
			// return true;
			point chc_p;
			if (a.p1 == b.p1) {
				// assert(!(a.p1 == b.p2));
				chc_p = b.p2;
			} else {
				chc_p = b.p1;
			}
			line chc_line1(a.p1, chc_p);

			if (is_parralel(l1, chc_line1)) {
				// cout << " 234";
				bool check = true;
				double min_x = min(a.p1.x, a.p2.x);
				double min_y = min(a.p1.y, a.p2.y);
				double max_x = max(a.p1.x, a.p2.x);
				double max_y = max(a.p1.y, a.p2.y);
				if (min_y <= b.p1.y && b.p1.y <= max_y
					&& min_x <= b.p1.x && b.p1.x <= max_x) {
					return true;
				}
				if (min_y <= b.p2.y && b.p2.y <= max_y
					&& min_x <= b.p2.x && b.p2.x <= max_x) {
					return true;
				}
				min_x = min(b.p1.x, b.p2.x);
				min_y = min(b.p1.y, b.p2.y);
				max_x = max(b.p1.x, b.p2.x);
				max_y = max(b.p1.y, b.p2.y);

				if (min_y <= a.p1.y && a.p1.y <= max_y
					&& min_x <= a.p1.x && a.p1.x <= max_x) {
					return true;
				}
				if (min_y <= a.p2.y && a.p2.y <= max_y
					&& min_x <= a.p2.x && a.p2.x <= max_x) {
					return true;
				}
				return false;
			} else {
				// cout << " 123-false\n";
				return false;
			}
		}
		point p = get_inter(l1, l2);

		// cout << p << nl;
		bool check = true;
		double min_x = min(a.p1.x, a.p2.x);
		double min_y = min(a.p1.y, a.p2.y);
		double max_x = max(a.p1.x, a.p2.x);
		double max_y = max(a.p1.y, a.p2.y);
		if (min_y <= p.y && p.y <= max_y
			&& min_x <= p.x && p.x <= max_x) {
		} else {
			check = false;
		}
		min_x = min(b.p1.x, b.p2.x);
		min_y = min(b.p1.y, b.p2.y);
		max_x = max(b.p1.x, b.p2.x);
		max_y = max(b.p1.y, b.p2.y);

		if (min_y <= p.y && p.y <= max_y
			&& min_x <= p.x && p.x <= max_x) {
		} else {
			check = false;
		}

		return check;
	}

	double get_area_sum(vector<segment> v) {
		double sm = 0;
		for (auto x : v) {
			sm += (x.p2.x - x.p1.x) * (x.p1.y + x.p2.y);
		}
		return abs(sm) / 2;
	}
}//namespace geo

