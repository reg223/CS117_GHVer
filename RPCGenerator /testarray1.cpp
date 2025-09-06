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

#include <string>
#include <iostream>
using namespace std;
#include "testarray1.idl"





int sqrt(int x[24][11], int y[24]) {
  return x[0][0] + y[0];
}

float hi(string lalala) {
  cout << lalala << endl;
  return 0.01;
}

Person findPerson(ThreePeople tp) {
  return tp.p1;
}

StructWithArrays test() {
  StructWithArrays res;
  res.aNumber = 114514;
  Person one = {"David", "Chen", 21};
  Person two = {"Sam", "Feng", 21};
  Person three = {"Tobias", "Fu", 21};
  res.people[0] = one;
  res.people[1] = two;
  res.people[2] = three;

  return res;
};

void DoesNothing(float Nothing) {
  cout << Nothing << endl;
}
void DoesSomeing(Person Nothing) {
  cout << Nothing.age << endl;
}
string getFirstString(string strs[5]) {
  return strs[1];
}

int getTotalAge(ThreePeople lots[10]) {
  int rtn = 0;
  for (int i = 0; i < 10; i++) {
    rtn += lots[i].p1.age;
    rtn += lots[i].p2.age;
    rtn += lots[i].p3.age;
    
  }
  return rtn;
}

int getNestedPerson(StructWithArrays arr[10][12]) {
  int rtn = 0;
  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < 12; j++) {
      rtn += arr[i][j].people[0].age;
      rtn += arr[i][j].people[1].age;
      rtn += arr[i][j].people[2].age;
      
    }
    
  }
  return rtn;
}