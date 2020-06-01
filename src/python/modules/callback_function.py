def myCommandCallback(cmd):
    print("Command received!")
    print("\tData: %s" % cmd.data)
    print("\tTimestamp: %s" % cmd.timestamp)
    print("\tCommandID: %s" % cmd.commandId)
    print("\tFormat: %s" % cmd.format)

    print("\nAdd your custom commands here!\n")
