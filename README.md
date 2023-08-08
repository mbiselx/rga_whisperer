# RGA Whisperer

This package is meant to enable the parsing of the datastream from a **Pfeiffer Vacuum QMG 200 Prisma Plus Residual Gas Analyzer**.

## Method 
The Pfeiffer Vacuum Prisma Plus QME 220 Residual Gas Analyzer (hereafter : RGA) runs Windows CE, which runs an OPC Data Access (OPC DA) server. 

There are multiple generations and versions of OPC. The OPC generation used by this device is OPC DA, also known as OPC Classic, and the version is version 3. 
OPC DA was developed to make use of Microsoft’s COM / DCOM technology. However, the RGA does not have a COM connection plug. Instead, it is meant to communicate through a network tunnel to a virtual COM port. For this, a tunnel must be set up between the RGA and the destination computer, and an OPC DA client run on the destination computer. 

Once this has been set up, the TCP traffic can be sniffed live using this library, or saved to a PCAP file (e.g. using [Wireshark](https://www.wireshark.org/)) and read later using this library. 

## Usage 
### Installation 
The package can be installed by cloning this repo, then running the following command in the repo's root : 
```
pip install .
```
Optionally, you can add the `-e` flag if you would like to edit the package (since it might not fulfill your needs).

### Examples 
Some usage examples can be found in this repo under [examples](./examples/).


## Notes On Setup
### Physical Interface 
The RGA must be interfaced via 100MBit ethernet on an RJ45 plug. The interface implements the IPV4 protocol, with the following IP address: 

> **IP Address** :  128.178.128.16  
> **Subnet Mask** : 255.255.255.0

The ethernet port of the receiving PC should be configured to suit this. I went with the following:
> **IP Address** :  128.178.128.55  
> **Subnet Mask** : 255.255.255.0

### OPC Tunneling
The only software which can set up the OPC TCP tunnel is the [dataFEED OPC Suite](https://industrial.softing.com/products/opc-opc-ua-software-platform/opc-server-middleware/datafeed-opc-suite-base.html) by Softing AG . At the time of writing, this software has a 72-hour runtime trial version available, which should run on Windows 7 and above .
The usage of the tunnelling software is described under heading *3.3.2. Tunnel Server Assistant* of the *LabView Installation Note*. In brief, one should create a “DA Tunnel Server” connected to the following address / port: 

> **Address**: tpda://128.178.128.16:56765

I was able to write a small Python script (annex 1) to reproduce the opening of the TCP tunnel. To do this, I inspected the network traffic on the ethernet connection using Wireshark and copied the necessary packets. 

### Client Interface Setup
The dataFEED OPC Suite by Softing AG also provides an OPC client, the “Softing OPC Classic Demo Client”. The heading *4.4 Testing the QMG Server* in the *Communication Protocol* describes how to connect and use the client, however, I found that slightly different steps were required, since the device did not show up under the “Manual” heading : 
1.	In the “OPC Servers” tab, under **Local**, select **Data Access V3**
2.	Under **Softing OPC dataFEED** heading, select the **Softing.OPC.DF.Configuration1.DA.1** source
3.	In the “DA Browse” tab, there will be two sources: “System” and “PrismaPlus”. Select **PrismaPlus**.

The OPC namespace should now be visible, as expected.
