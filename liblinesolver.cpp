#include <iostream>
#include <vector>
#include <array>

using namespace std;

bool check_point(double *p1, double *p2, double *cp)
{
    return true;
//    <vector>d = <vector>p2 - <vector>p1;

//    l, m, n = d;

//    double x1 = p1[0];
//    double y1 = p1[1];
//    double z1 = p1[2];

//    x, y, z = np.array(cp);

//    if (l == 0){
//        if (x != x1){
//            return false;
//        }
//        else if (n * y - n * y1 == m * z - m * z1){
//            return true;
//        }
//        else{
//            return false;
//        }
//    }

//    if (m == 0) {
//        if (y != y1) {
//            return false;
//        }
//        else if(n * x - n * x1 == l * z - l * z1){
//            return true;
//        }
//        else{
//            return false;
//        }
//    }

//    if (n == 0) {
//        if (z != z1){
//            return false;
//        }
//        else if (m * x - m * x1 == l * y - l * y1){
//            return true;
//        }
//        else{
//            return false;
//        }
//    }

//    if ((n * y - m * z + (m * z1 - n * y1)) == 0 and (m * x - l * y + (l * y1 - m * x1)) == 0){
//        return true;
//    }

//    else{
//        return false;
//    }
}

extern "C"
{
    extern bool cffi_check_point(double *p1, double *p2, double *cp)
    {
        return check_point(p1, p2, cp);
    }
}
