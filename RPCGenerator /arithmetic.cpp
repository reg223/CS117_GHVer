// --------------------------------------------------------------
//
//                        arithmetic.cpp
//
//        Author: Noah Mendelsohn         
//   
//
//        Trivial implementations of the routines declared
//        in arithmetic.idl. These are for testing: they
//        just print messages.
//
//       Copyright: 2012 Noah Mendelsohn
//     
// --------------------------------------------------------------

// IMPORTANT! WE INCLUDE THE IDL FILE AS IT DEFINES THE INTERFACES
// TO THE FUNCTIONS WE'RE IMPLEMENTING. THIS MAKES SURE THE
// CODE HERE ACTUALLY MATCHES THE REMOTED INTERFACE

#include "arithmetic.idl"
#include <string>
#include <iostream>
using namespace std;




int add(int x, int y) {
  return x+y;
}

int subtract(int x[5], int y[5]) {
  int res= 0;
  for (int i = 0; i < 5; i++){
    cout << "curr x: " << x[i] << endl;
    cout << "curr y: " << y[i] << endl;
    res += x[i]-y[i];
  }
  
  return res;
}

int multiply(int x, int y) {
  return x*y;
}

int divide(int x, int y) {
  return x/y;
}


