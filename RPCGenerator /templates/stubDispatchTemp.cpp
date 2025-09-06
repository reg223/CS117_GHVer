if (strcmp(functionNameBuffer,"{funcname}") == 0) {{

*GRADING << "Entered dispatch function for <{funcname}>!"  << endl;

//====================
//   READ PARAMETERS
//====================
char size[4];
int size_int = 0;
int fetchoffset = 0;
int intbuff = 0;
int strleng = 0; // for temporary storage of incoming string's length

// Read from client to get parameters
RPCSTUBSOCKET->read(size, sizeof(size));
memcpy(&intbuff, size, 4);
size_int  = ntohl(intbuff);
// Avoid empty arrays for functions with no parameters
if (size_int != 0) {{
  char readBuffer[size_int];
  RPCSTUBSOCKET->read(readBuffer, size_int);
*GRADING << "<{funcname}> Parsing nonempty parameter buffer of "<< size_int 
         << " bytes;"  << endl;
  //Create Instances of each paramater received

  {paramDeclaration}

  //Copy from buffer, fill each instance

  {fillParams}
  //Call stub with filled parameters
  {callStub}
}}else {{
*GRADING << "<{funcname}>  has no input arguments, calling function"  << endl;
  {paramDeclaration}
  {trivialDec}
  //Call stub 
  {callStub}
}}


*GRADING << "exiting dispatch function for<{funcname}>."  << endl;
(void) strleng; // in case there's no string
(void) fetchoffset;
}} 



