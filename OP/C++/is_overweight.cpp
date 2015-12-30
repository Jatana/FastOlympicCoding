template<typename T>
bool can_add(const T& a, const T& b) {
	return b <= (std::numeric_limits<T>::max() - a);
}

template<typename T>
bool can_sub(const T& a, const T& b) {
	return b <= (std::numeric_limits<T>::min() + a);
}

template<typename T>
bool can_mul(const T& a, const T& b) {
	return (b <= (std::numeric_limits<T>::max() / a)) && 	
	       (b >= (std::numeric_limits<T>::min() / a));
}

template<typename T>
bool can_div(const T& a, const T& b) {
	return (a <= (std::numeric_limits<T>::max() * b)) && 
	       (a >= (std::numeric_limits<T>::min() * b));
}