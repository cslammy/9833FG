from pyftdi.spi import SpiController


############user changes these###############
user_freq = 1000

#pinout from H232 for SPI
'''
ad0 SCLK to UNO pin 13
ad1 MOSI to UNO pin     11
ad2 MISO to UNO pin 12 (not used)
ad3 CS0 to UNO pin 10
ad4 cs1 ... ad7 CS4.
'''
#WE WANT TO BE ABLE TO ENTER A FREQ TO SHOW ON SCOPE.
# Instantiate a SPI controller
# We need want to use A*BUS4 for /CS, so at least 2 /CS lines should be
# reserved for SPI, the remaining IO are available as GPIOs.


def get_dec_freq(freq):
    bignum = 2**28
    f = freq
    clock=25000000 #if your clock is different enter that here./
    dec_freq = f*bignum/clock
    return int(dec_freq)


padded_binary = 0
bits_pushed = 0
d = get_dec_freq(user_freq)

print("freq int returned is: " + str(d))

#turn into binary string.
str1 = bin(d)
#print(str1)

#get rid of first 2 chars.
str2 = str1[2:]
#print(str2)

#pad whatever we have so far to 28 bits:
longer = str2.zfill(28)
#print("here is 28 bit version of string")
#print(str(longer))
#print("here is length of that string")
#print(len(str(longer)))

lm1 = "01" + longer[:6]
lm2 = longer[6:14]
rm1 = "01" + longer[14:20]
rm2 = longer[20:]
# print(lm1 + " " + lm2  + " " + rm1 + " " + rm2)


def str_2_int(strx):
    numb = int(strx, 2)
    return numb

lm1x = str_2_int(lm1)
lm2x = str_2_int(lm2)
rm1x = str_2_int(rm1)
rm2x = str_2_int(rm2)
print(str(lm1x) + " " + str(lm2x)  + " " + str(rm1x) + " " + str(rm2x))

##########
#freq0_loadlower16 = [80,199]
#freq0_loadupper16 = [64,0]
#64 0 80 198


spi = SpiController(cs_count=2)
device = 'ftdi://ftdi:232h:0:1/1'
# Configure the first interface (IF/1) of the FTDI device as a SPI master
spi.configure(device)

# Get a port to a SPI slave w/ /CS on A*BUS4 and SPI mode 2 @ 10MHz
slave = spi.get_port(cs=1, freq=8E6, mode=2)


freq0_loadlower16 = [rm1x,rm2x]
freq0_loadupper16 = [lm1x,lm2x]

cntrl_reset = [33,0]


phase0 = [192,0]

#cntrl_write = [32,0]  #sine
#cntrl_write = [32,2]  #tri
cntrl_write = [32,32]  #square
send2_9833 = cntrl_reset + freq0_loadlower16 + freq0_loadupper16 + phase0 + cntrl_write

print(send2_9833)

qq = bytearray(send2_9833)
# Synchronous exchange with the remote SPI slave
#write_buf = qq
#read_buf = slave.exchange(write_buf, duplex=False)
slave.exchange(out=qq, readlen=0, start=True, stop=True, duplex=False, droptail=0)
slave.flush()
