from Registry import Registry
import sys

reg = Registry.Registry("triage/registry/Amcache.hve")

def print_key(key, depth=0):
    print("  " * depth + key.name())
    for sub in key.subkeys():
        if depth < 2:
            print_key(sub, depth + 1)

print("Root subkeys:")
for k in reg.root().subkeys():
    print(" ", k.name())
