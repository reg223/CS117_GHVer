
{funcHeader} {{

*GRADING << "Entered function <{funcName}>!"  << endl;
//Foward declaration
int sendsize = 0; //to log the total size of the function been sent
int offset = 0; // used for compiling the stream
int intbuff = 0;// temporarily stores int in sending format

//====================
//   SEND PARAMETERS
//====================
{getSize}

char sendBuff[sendsize+sizeof("{funcName}")+4];

// Compiling Send Header (function name + size of Param)

{sendHeader}

// Compiling Parameters into send buffer

{writeSend}
*GRADING << "function <{funcName}> sent " << sizeof(sendBuff) 
         << " bytes of information to server"  << endl;
RPCPROXYSOCKET->write(sendBuff, sizeof(sendBuff));


//====================
//   READ RETURN
//====================

// Retrieve return result from stream
int returnsize = 0; //to record size of the returned Object
char sizeBuffer[4]; //trivial holder for returnsize
int fetchoffset = 0;//for unloading components of returned object
int strleng = 0;

RPCPROXYSOCKET->read(sizeBuffer, 4);
memcpy(&intbuff,sizeBuffer,4);
returnsize = ntohl(intbuff);


char readBuffer[returnsize];
RPCPROXYSOCKET->read(readBuffer, returnsize);
*GRADING << "function <{funcName}> received " << sizeof(returnsize) 
         << " bytes of information from server"  << endl;

{returnType} res; // called res regardless of type 

// Rebuild return result from stream
{fillInstance}

*GRADING << "Function <{funcName}> completed, exiting"  << endl;
(void) strleng;
return {res};
}}
