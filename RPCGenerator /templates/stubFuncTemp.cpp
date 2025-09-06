{funcHeader} {{
*GRADING << "Entered stub function <{funcHeader}>"  << endl;
// make call to actual function and retrieve returned object 
// or "Done" for void functions
{retrieveRes}
*GRADING << "stub function <{funcHeader}> returned from calling function, compiling results"  << endl;
int sendsize = 0;// records size of returned object
int offset = 4;// records offset, first value in buffer is always size
int intbuff = 0;


// computes size of result
{updateSize}

char sendBuff[sendsize + 4];
intbuff = htonl(sendsize);
memcpy(sendBuff,&intbuff,4);

// fill the buffer using retrieved Object
{fillBuffer}
RPCSTUBSOCKET->write(sendBuff, sendsize+4);
*GRADING << "stub function <{funcHeader}> sent a total of " << sendsize+4 
         << "bytes to client, exiting." << endl;
(void) sendsize;
(void) offset;
(void) intbuff;
}}
