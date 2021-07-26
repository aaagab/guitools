#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    msg = importlib.import_module(module_name)
    del sys.path[0]

    msg.clear(scroll=True)
    print("scrolling history has been erased")

    msg.clear()
    print("screen has been cleared")

    msg.info("This is a single line info")
    print()
    msg.info([
        "This is a multiline info",
        "This is a multiline info",
        "This is a multiline info"
    ])
    print()

    mylist=[ 
        "line one '{}'", 
        "line two '{}'", 
        "line tree '{}'" ]
    msg.info("A list is given \"{}\" instead of multiple lines".format(mylist))
    print()
    msg.info(mylist)
    print()

    keys=["first_value", "second_value", "third_value"]
    msg.info("keys list \"{}\" is given to populate empty fields '{{}}'".format(keys,))
    print()
    msg.info(mylist, keys=keys)
    print()

    mylist=[ 
        "line one '{first}'", 
        "line two '{second}'", 
        "line tree '{first} and '{third}''" 
    ]
    print()
    keys={
        "first":"first_value", 
        "second":"second_value", 
        "third":"third_value"
    }
    msg.info("It also work with keywords")
    msg.info(mylist)
    print()
    msg.info(mylist, keys=keys)
    print()

    text_heredoc="""
            this is an heredoc:
              - with 'another' text
              - and another text
              - and a variable '{key}'
    """
    msg.info("non-formatted heredoc")
    print(text_heredoc)

    msg.info("formatted heredoc")
    msg.info(text_heredoc, heredoc=True, keys=dict(key="myVariable"))
    print()
    msg.error(text_heredoc, heredoc=True, keys=dict(key="myVariable"))
    print()

    msg.warning("This is a single line warning")
    print()

    msg.warning([
        "This is a multiline line warning",
        "This is a multiline line warning",
        "This is a multiline line warning"
    ])
    print()

    msg.success("This is a single line success")
    print()

    msg.success([
        "This is a multiline line success",
        "This is a multiline line success",
        "This is a multiline line success"
    ])
    print()

    msg.info(r"""
        Pretty print can be disabled.
        Pretty is automatically disabled:
        - if output is captured from inside another program.
        - if output is piped into another command.
    """, heredoc=True, pretty=False)
    print()

    msg.success("No Pretty", pretty=False)
    msg.warning("No Pretty", pretty=False)
    msg.error("No Pretty", pretty=False)
    print()

    msg.info("A prefix can be added", prefix="ADDED PREFIX")
    msg.info("A prefix can be added", prefix="ADDED PREFIX", pretty=False)
    print()

    msg.error("This is a single line error")
    print()
    msg.error([
        "This is a multiline error",
        "This is a multiline error",
        "This is a multiline error",
    ])
    print()
    msg.error("This is a single error with stack trace", trace=True)
    print()
    
    msg.error([
        "This is a multiline error with stack trace",
        "This is a multiline error with stack trace",
        "This is a multiline error with stack trace",
    ], trace=True)
    print()

    msg.error("This is an error with stack trace and system exit with code 1", exit=1, trace=True)

    # To test stderr and stdout put that in another file
    # import subprocess
    # proc=subprocess.Popen(["./samples.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr=proc.communicate()
    # print(stdout)
    # print(stderr)
    # print(proc.returncode)
 