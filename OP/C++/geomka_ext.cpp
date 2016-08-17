namespace geo {
#define double long double

const double EPS = 0.0000001;


double to_radians(double ang_deg) {
	return (ang_deg * M_PI / 180.0);
}

double to_degrees(double ang_rad) {
	return (ang_rad * 180.0 / M_PI);
}

bool eq(double a, double b = 0) {
	return abs(a - b) <= EPS;
}


class line;
class point;


class point {
public:
	double x, y;
	
	inline point() {}

	inline point(double _x, double _y):x(_x), y(_y) {}
	
	void set_polar(double _angle, double _dist) {
		x = cos(_angle) * _dist;
		y = sin(_angle) * _dist;
	}

	double length() {
		return sqrt(x * x + y * y);
	}

	double angle() {
		return atan2(y, x);
	}

	friend istream &operator,(istream &is, point &p) {
		scan p.x, p.y;
		return is;
	}

	friend point operator-(point p1, point p2) {
		return point(p1.x - p2.x, p1.y - p2.y);
	}

	void operator-=(const point &p) {
		x -= p.x;
		y -= p.y;
	}

	point operator/(double d) {
		return point(x / d, y / d);
	}

	point operator*(double d) {
		return point(x * d, y * d);
	}

	void operator/=(double d) {
		x /= d;
		y /= d;
	}

	void operator*=(double d) {
		x *= d;
		y *= d;
	}

	point rotate90() {
		return point(-y, x);
	}

	point invert() {
		return point(-x, -y);
	}

	void set_length(double l) {
		double cur_len = length();
		x /= cur_len;
		y /= cur_len;
		x *= l;
		y *= l;
	}

	double operator*(const point &p) {
		return (x * p.x + y * p.y);
	}

	double operator^(point &p) {
		return (x * p.y - y * p.x);
	}

	point operator+(point p) {
		return point(x + p.x, y + p.y);
	}

	void operator+=(point p) {
		x += p.x;
		y += p.y;
	}
	
	friend ostream &operator,(ostream &os, const point &p) {
		os, p.x, p.y;
		return os;
	}

	bool operator==(point p) {
		return eq(x, p.x) && eq(y, p.y);
	}

	bool operator<(const point &p) const {
		return vector<double>{x, y} < vector<double>{p.x, p.y};
	}

	double angle_to(point p) {
		return acos(((*this) * p) / (p.length() * length()));
	}
};


class line {
public:
	double a, b, c;

	line() {}

	line(double _a, double _b, double _c):a(_a), b(_b), c(_c) {}

	line(point p1, point p2) {
		set_abc(p1, p2);
	}

	void set_abc(point p1, point p2) {
		point p = p1 - p2;
		a = p.y;
		b = -p.x;
		c = -(a * p1.x + b * p1.y);	
	}

	double equate(point p) const {
		return a * p.x + b * p.y + c;
	}

	double distance(point p) {
		return abs((a * p.x + b * p.y + c) / (point(a, b).length()));
	}

	point intersect(line l) {
		double x = (-l.b * c + l.c * b) / (a * l.b - b * l.a);
		double y = (-a * l.c + c * l.a) / (-b * l.a + a * l.b);
		// cout << *this << ":" << l << "}";
		// cout << x << " " << y << " ";
		return point(x, y);
	}

	// point intersect2(line l) {
		// 
	// }

	double get_x(double y) {
		return (-b * y - c) / a;
	}

	double get_y(double x) {
		return (-a * x - c) / b;
	}
	
	void move(point dp) {
		// cout << dp << nl;
		// double new_y = (-c / b) + dp.y;
		// c = -new_y * b;

		// double new_x = (-c / a) + dp.x;
		// c = -new_x * a;
		// cout << *this << nl;
		// assert(!eq(b));

		point inline_p1;
		point inline_p2;
		if (!eq(b)) {
			assert(!eq(b));
			inline_p1 = point(0, get_y(0));
			inline_p2 = point(1, get_y(1));
		} else {
			assert(!eq(a));
			inline_p1 = point(get_x(0), 0);
			inline_p2 = point(get_x(1), 1);
		}
		inline_p1 += dp;
		inline_p2 += dp;
		set_abc(inline_p1, inline_p2);
	}


	friend ostream &operator<<(ostream &os, line &l) {
		os << l.a << " " << l.b << " " << l.c;
		return os;
	}

	friend istream &operator>>(istream &is, line &l) {
		is >> l.a >> l.b >> l.c;
		return is;
	}
};

class segment {
public:
	point first, second;

	segment() {}
	
	segment(point _first, point _second): first(_first), second(_second) {}

	double distance(point p) {
		double cos1 = ((first - second) * (p - second)) / ((first - second).length() * (p - second).length());
		double cos2 = ((second - first) * (p - first)) / ((second - first).length() * (p - first).length());
		// cout << cos1 << " " << cos2 << nl;
		if (cos1 >= 0 && cos2 >= 0) {
			return (line(first, second)).distance(p);
		} else {
			return min((first - p).length(), (second - p).length());
		}
	}

	bool in_segment(point p) {
		// cout << abs((first - second).length() -
		// 	(first - p).length() + (second - p).length());
		return abs((first - second).length() -
			(first - p).length() - (second - p).length()) < EPS;
	}

	bool intersect(segment s) {
		point p = line(s.first, s.second).intersect(line(first, second));
		return this->in_segment(p) && s.in_segment(p);
	}

	friend istream&operator,(istream &is, segment &s) {
		is, s.first, s.second;
		return is;
	}
};

class circle {
public:
	double radius;
	point center;


	circle() {}
	circle(point _center, double _radius): center(_center), radius(_radius) {}
	

	double equate(point p) {
		// p = p - center;
		double x = p.x;
		double y = p.y;
		return x * x + y * y - radius * radius;
	}

	vector<point> tangent(point p) {
		assert(radius > 0);
		p -= center;
		if (p.length() < radius) {
			// cout << p.length() << nl;
			// assert(false);
			return vector<point>();
		}
		if (p.length() == radius) {
			vector<point> rez;
			rez.push_back(p + center);
			return rez;
		}
		vector<point> rez;
		// cout << radius << " : " << p.length() << nl;
		double tgp_len = sqrt(p.length() * p.length() - radius * radius);
		double alpha = asin(radius / p.length());
		// cout << tgp_len << " " << p.length() << nl;
		// cout << to_degrees(alpha) << nl;
		point sub_center = point(p.x, p.y);
		point inter;
		inter.set_polar(sub_center.angle() + alpha, tgp_len);
		// cout << inter << nl;
		rez.push_back(p - inter + center);
		inter.set_polar(sub_center.angle() - alpha, tgp_len);
		rez.push_back(p - inter + center);
		return rez;
	}

	vector<point> intersects_with_equasion(line l) {
		l.move(center.invert());
		// cout << l << nl;
		double a = l.b * l.b + l.a * l.a;
		double b = 2 * l.b * l.c;
		double c = l.c * l.c - l.a * l.a * radius * radius;
		double descr = b * b - 4 * a * c;
		if (descr < 0) return {};
		double root1 = (-b + sqrt(descr)) / (2 * a);
		double root2 = (-b - sqrt(descr)) / (2 * a);
		vector<point> rez;
		auto check_root = [&rez, l, descr](double root, circle _circle){
			double x = sqrt(_circle.radius * _circle.radius - root * root);
			double y = root;
			x = (-l.b * y - l.c) / l.a;
			// cout << x << " " << y << nl;
			double in_equate1 = x * x + y * y;
			double in_equate1_rez = _circle.radius * _circle.radius;
			// cout << t << " " << t2 << " " << " " << eq(t, t2) << endl;
			// cout << l.equate(point(x, y)) << endl;
			if (eq(_circle.equate(point(x, y))) && 
				eq(l.equate(point(x, y)))) {
				rez.push_back(_circle.center + 
					point(x, y));
			}
		};

		check_root(root1, *this);
		check_root(root2, *this);
		if (rez.size() > 1) {
			if (eq(rez[0].x, rez[1].x) && eq(rez[0].y, rez[1].y)) {
				rez.ppb();
			}
		}
		return rez;
	}

	vector<point> intersects(line l) {
		l.move(center.invert());
		double min_dist = l.distance(point(0, 0));
		point pt_normal(l.a, l.b);
		pt_normal /= pt_normal.length();
		pt_normal *= min_dist;
		if (!eq(l.equate(pt_normal))) {
			pt_normal = pt_normal.invert();
		}
		if (pt_normal.length() > radius) {
			return {};
		}
		if (eq(min_dist, radius)) {
			return {center + pt_normal};
		}
		double d = sqrt(radius * radius - min_dist * min_dist);
		point inline_pt(-l.b, l.a);
		inline_pt.set_length(d);
		vector<point> rez;
		rez.push_back(center + pt_normal + inline_pt);
		rez.push_back(center + pt_normal - inline_pt);
		return rez;
	}

	vector<point> intersects(circle c) {
		double betw_dist = (center - c.center).length();
		
		if (c.center == center && radius == c.radius)
			throw "To More Intersections";

		if (betw_dist > c.radius + radius)
			return {};

		if (betw_dist + radius < c.radius)
			return {};

		if (betw_dist + c.radius < radius) 
			return {};

		if (eq(betw_dist + c.radius, radius)) {
			point pt(c.center - center);
			pt.set_length(pt.length() + c.radius);
			return {center + pt};
		}

		if (eq(betw_dist + radius, c.radius)) {
			point pt(center - c.center);
			pt.set_length(pt.length() + radius);
			return {c.center + pt};
		}

		if (eq(betw_dist, c.radius + radius)) {
			point pt(c.center - center);
			pt.set_length(radius);
			return {center + pt};
		}
		double cx = c.radius;
		double b = (c.center - center).length();
		double a = radius;
		double alpha = (a * a + b * b - cx * cx) / (2 * a * b);
		double d = radius * alpha;
		double norm_d = sqrt(radius * radius - d * d);
		// cout << a << " " << b << " " << cx << nl;
		// cout << d << nl;
		point pt = c.center - center;
		pt.set_length(d);
		point norm_pt = pt.rotate90();
		norm_pt.set_length(norm_d);
		vector<point> rez;
		rez.pb(center + pt + norm_pt);
		rez.pb(center + pt - norm_pt);
		if (eq(rez[0].x, rez[1].x) && eq(rez[0].y, rez[1].y)) {
			rez.ppb();
		}
		return rez;
	}

	friend istream &operator>>(istream &is, circle &c) {
		is, c.center, c.radius;
		return is;
	}
};

template<class T>
T get_value_factor(T x) {
	if (x > (T)0) {
		return (T)1;
	} elif(x < (T)0) {
		return (T)-1;
	}
	return (T)0;
}

class polygon {
public:
	vector<point> points;
	
	polygon(vector<point> _points):points(_points) {}

	bool in_side(point p) {
		double summary_angle = 0;
		for (int i = 0; i < points.size(); i++) {
			if (segment(points[i], points[(i + 1) % points.size()]).in_segment(p)) {
				return true;
			}
			point p1 = points[i] - p;
			point p2 = points[(i + 1) % points.size()] - p;
			double sin_alpha = ((p1 ^ p2) / (p1.length() * p2.length()));
			double factor = get_value_factor(sin_alpha);
			summary_angle += abs(asin(sin_alpha)) * factor;
		}
		// cout << summary_angle << nl;
		return abs(summary_angle) > 1;
	}

	bool in_side_with_ray(point p) {
		point magic_point(123456, 666666);
		// point magic_point(4, 2);
		segment s(p, magic_point);
		int cnt = 0;
		for (int i = 0; i < points.size(); i++) {
			segment edge(points[i], points[(i + 1) % points.size()]);
			if (edge.in_segment(p) == true) {
				return true;
			}
			cnt += edge.intersect(s);
		}
		// cout << cnt << nl;
		return cnt & 1;
	}

	bool is_convex() {
		int n = points.size();
		double last_turn = 0;
		for (int i = 0; i < n; i++) {
			point p1 = points[i];
			point p2 = points[(i + 1) % n];
			point p3 = points[(i + 2) % n];
			point p = p1 - p2;
			point q = p3 - p2;
			double sin_alpha = (p ^ q) / (p.length() * q.length());
			if (last_turn == 0) {
				last_turn = get_value_factor(sin_alpha);
				continue;
			}
			if (last_turn != get_value_factor(sin_alpha)) {
				return false;
			}
		}
		return true;
	}

	double square() {
		double sq = 0;
		for (int i = 0; i < points.size(); i++) {
			point first = points[i];
			point second = points[(i + 1) % points.size()];
			double w = second.x - first.x;
			double up_h = second.y - first.y;
			sq += w * first.y + (w * up_h / 2);
		}
		return abs(sq);
	};
};

line create_line_with_normal(point norm, point p_in_line) {
	double a = norm.x;
	double b = norm.y;
	double c = -(a * p_in_line.x + b * p_in_line.y);
	return line(a, b, c);
}



vector<point> convex_hull(vector<point> points, int kostil_id = 8) {
	point down = points[0];
	int n = points.size();
	if (n == 1) {
		return vector<point>{points[0]};
	}
	int down_ind = 0;
	for (int i = 1; i < n; i++) {
		point p = points[i];
		if (p.y == down.y) {
			if (p.x > down.x) {
				down = p;
				down_ind = i;
			}
		} elif(p.y < down.y) {
			down = p;
			down_ind = i;
		}
	}
	tie(points[down_ind], points[n - 1]) 
		= mt(points[n - 1], points[down_ind]);
	points.ppb();
	// cout << points << ":\n";
	for (auto x : points) {
		// cout << (x - down).angle() << " ";
	}
	// cout << "::\n";
	// cout << down << "::\n";
	// cout << "NL\n";
	// cout << points << ":\n";
	n = points.size();
	sort(points.begin(), points.end(), [&down, &kostil_id](point a, point b){
		point p = a - down;
		point q = b - down;
		if (p.angle() == q.angle()) {
			// cout << "applyied\n";
			// if (kostil_id == 5) {
			// 	return p.length() < q.length();
			// }
			return p.length() < q.length();
		}
		return p.angle() < q.angle();
	});
	// cout << points << nl;
	vector<point> rez;
	rez.pb(down);
	rez.pb(points[0]);
	// cout << "down: ";
	// cout << down << nl;
	for (int i = 1; i < n; i++) {
		bool need_iter = true;

		need_iter = true;
		point p1 = rez[rez.size() - 2], p2 = rez[rez.size() - 1];
		point p = p1 - p2;
		point q = points[i] - p2;
		// cout << p1 << " " << p2 << " " << points[i] << nl;
		while (((rez.size() >= 2)) && (p ^ q) >= 0) {
			// cout << (p ^ q) << endl;
			rez.ppb();
			p1 = rez[rez.size() - 2], p2 = rez[rez.size() - 1];
			p = p1 - p2;
			q = points[i] - p2;
		}

		rez.pb(points[i]);
	}
	point p1 = rez[rez.size() - 2], p2 = rez[rez.size() - 1];
	point p = p1 - p2;
	point q = down - p2;
	while ((rez.size() >= 3) && (p ^ q) >= 0) {
		rez.ppb();
		p1 = rez[rez.size() - 2], p2 = rez[rez.size() - 1];
		p = p1 - p2;
		q = down - p2;
	}
	return rez;
}
} // namespace geo


using namespace geo;