def fixValue(fixCol, fixVal):
    return DATA.loc[DATA[fixCol] == fixVal]

def countNaN(fixedDF):
    return fixedDF["RF Output/dBm"].isnull().values.sum()

totalNaN = DATA["RF Output/dBm"].isnull().sum()
print("total: ", totalNaN)


print("AM")
for v in amvolt:
    print(countNaN(fixValue("AM Volt/V", v)))

print("SET FREQ")
for f in freqs:
    c = countNaN(fixValue("# Set Freq/MHz", f))
    print(f, c)


freqs    = DATA["# Set Freq/MHz"].unique()
rfintput = DATA["RF Input/dBm"].unique()
amvolt   = DATA["AM Volt/V"].unique()