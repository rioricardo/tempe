import os
import subprocess
import sys
import platform
import shutil
import argparse


# Get the current script path
current_dir = os.path.dirname(__file__)
# Get the parent directory
parent_dir = os.path.dirname(current_dir)

binout = os.path.join(parent_dir,'bin')
libout = os.path.join(parent_dir,'lib')

#help and usage
def setup_parser():
    """Setup argument parser to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Automates the process of compiling C++ programs and libraries based on a build configuration file."
    )
    
    # Add arguments for specifying directories to compile
    parser.add_argument(
        'directories', 
        nargs='*',  # Accept zero or more directories
        help="Directories to compile. If none provided, all directories in the build file will be processed."
    )
    
    # Optional argument for --help (automatically handled by argparse)
    parser.add_argument(
        '--version', 
        action='version', 
        version="1.0",  # Replace with your script version
        help="Show the version of the script."
    )
    
    return parser

# detect the system compiler
# O : string of compiler name
def detect_compiler():
    """Detect the system compiler."""
    system_platform = platform.system()
    if system_platform in ["Linux", "Darwin"]:
        compiler = shutil.which("g++")
        if compiler:
            return "g++"
        else:
            raise EnvironmentError("No suitable C++ compiler found on Linux or macOS.")
         
    elif system_platform == "Windows":
        compiler = shutil.which("g++") or shutil.which("cl")
        if compiler:
            return compiler
        else:
            raise EnvironmentError("No suitable C++ compiler found on Windows.")
    else:
        raise EnvironmentError("Unknown platform")

# procedure to create lib directories and bin directories
def prepare_directories(bindir):
    """Ensure the binary directory exists, creating it if necessary."""
    if not bindir:
        raise ValueError("Binary directory path is missing.")
    try:
        os.makedirs(bindir, exist_ok=True)
    except Exception as e:
        print(f"Error creating binary directory '{bindir}': {e}")
        sys.exit(1)

def check_compile_directory(parent_dir,objdir):
    compdir = os.path.join(parent_dir, objdir)
    if not os.path.isdir(compdir):
        print(f"invalid program or library directory '{compdir}'.")
        return
    return compdir


#bldfile processes

def search_bldfile(comp_dir,bldfile):
    bldfilename = os.path.join(comp_dir,bldfile)
    if not os.path.isfile(bldfilename):
        print(f"bld file not found '{bldfilename}'.")
        return
    return bldfilename

def read_bldfile(bldfilename):
    """Load and parse the build file, returning program configuration dictionaries."""
    objdic, typdic, srcdic, filedic, libdic, optdic = {}, {}, {}, {}, {}, {}
    obj = None
    try:
        with open(bldfilename, "r") as bldfile:
            for line in bldfile:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if '=' in line:
                    id, value = (part.strip() for part in line.split('=', maxsplit=1))
                    if id == 'prog':
                        objdic[value] = value
                        typdic[value] = 'prog'
                        obj = value
                    elif id == 'dynlib':
                        objdic[value] = value
                        typdic[value] = 'dynlib'
                        obj = value
                    elif id == 'statlib':
                        objdic[value] = value
                        typdic[value] = 'statlib'
                        obj = value
                    elif id == 'dir':
                        if(obj):
                            srcdic[obj] = value
                        else:
                            print (f"no object file found for {id} and {value}")
                    elif id == 'file':
                        if(obj):
                            filedic[obj] = value
                        else:
                            print (f"no object file found for {id} and {value}")
                    elif id == 'libraries':
                        if(obj):
                            libdic[obj] = value
                        else:
                            print (f"no object file found for {id} and {value}")
                    elif id == 'option':
                        if(obj):
                            optdic[obj] = value
                        else:
                            print (f"no object file found for {id} and {value}")
    except FileNotFoundError:
        print(f"Error: {bldfilename} does not exist.")
    except Exception as e:
        print(f"Error reading {bldfilename}: {e}")
    
    return objdic, typdic, srcdic, filedic, libdic, optdic

def check_objects_in_bldfile(bldfile,objdic,typdic):
    if not objdic or not typdic:
        print (f"no objects found in {bldfile}")
        return False
    return True

def process_bldfile(comp_dir,bldfile='Bldfile'):
    bldfilevalid = True
    #search for bldfile
    bldfile = search_bldfile(comp_dir, bldfile)
    if not bldfile : 
        bldfilevalid = False
    #read bldfile 
    objdic, typdic, srcdic, filedic, libdic, optdic = read_bldfile(bldfile)
    #validate objects in bldfile
    if not check_objects_in_bldfile(bldfile, objdic, typdic): 
        bldfilevalid = False
        
    return bldfilevalid, objdic, typdic, srcdic, filedic, libdic, optdic

#end of bldfile processes

#compilation processes

#procedure to compile program
def compile_program(incdir, libraries, compiler, type, source_files, output_path, options):
    """Compile the program using the specified compiler and source files."""
    if type == 'prog':
        compile_command = [compiler] + source_files + libraries + [opt for opt in [options, incdir, "-g", "-o", output_path] if opt]
    elif type == 'dynlib':
        compile_command = [compiler] + source_files + libraries + [opt for opt in [incdir, options, "-fPIC", "-shared","-g", "-o", output_path] if opt]
    elif type == 'statlib':
        compile_command = [compiler] + source_files + libraries + [opt for opt in [incdir, options,"-g", "-o", output_path] if opt]
    else:
        print(f"Error: unknown type of object {output_path}, skip compiling")
        return
    try:
        print(f"Compiling {output_path}...")
        print(f"Compile command {compile_command}...")
        subprocess.run(compile_command, check=True)
        print(f"Build successful! Binary created at {output_path}")
    except subprocess.CalledProcessError:
        print(f"Error: Compilation failed for {output_path}")
        return

def check_src_directory(cmpdir,src):
    if not src:
        return cmpdir
    cmpdir = os.path.join(cmpdir, src)
    if not os.path.isdir(os.path.join(cmpdir)):
        print(f"file {cmpdir}/{src} not found, skipping {cmpdir}")
        return
    return cmpdir

def collect_sources(cmpdir, src, files):
    cmpdir = check_src_directory(cmpdir,src)
    if not cmpdir:
        return
    source_files = []
    for f in (part.strip() for part in files.split(';')):
        if os.path.isfile(os.path.join(cmpdir, f)):
            source_files.append(os.path.join(cmpdir, f))
        else :
            print(f"file {cmpdir}/{f} not found, skipping {cmpdir}")
            return
    return source_files

def validate_options(options):
    if (options):
        return ' '.join(part.strip() for part in options.split(';'))
    else:
        return
  
def get_libraries(libout, libs):
    #link custom library in compilation
    libraries = []
    custlib = "-L" + os.path.join(libout)
    if (libs):
        libraries = [f"-l{l}" for l in libs.split(';')]
        libraries = [custlib] + libraries + [f"-Wl,-rpath,{libout}"]
    return libraries

def addinclude(parent_dir):
    #add includes 
    return "-I" + os.path.join(parent_dir)

# I: program name according to bldfile and the type
def get_binary_name(binout, libout, prog_name,type):
    """Get the appropriate binary name based on the operating system."""
    system_platform = platform.system()
    if type == 'prog':
        progname = f"{prog_name}.exe" if system_platform == "Windows" else prog_name
        return os.path.join(binout,progname)
    elif type == 'dynlib':
        if system_platform == 'Darwin':
            libname = f"lib{prog_name}.dylib"
        else:
            libname = f"lib{prog_name}.dll" if system_platform == "Windows" else f"lib{prog_name}.so"
        return os.path.join(libout,libname)
    elif type == 'statlib':
        libname = f"lib{prog_name}.lib" if system_platform == "Windows" else f"lib{prog_name}.a"
        return os.path.join(libout,libname)
    else:
        print(f"Error: unknown type of object {prog_name}")
        return

#procedure to build program
def build_program(parent_dir, comp_dir, binout, libout, compiler, objdic, typdic, srcdic, filedic, libdic, optdic):
    #find the type of compiler
    for obj in objdic:
        type = typdic.get(obj)
        output_path = get_binary_name(binout, libout, obj,type)
        if not output_path: next
        src = srcdic.get(obj)
        files = filedic.get(obj)
        option = optdic.get(obj)
        libs = libdic.get(obj)

        #add include directory
        incdir = addinclude(parent_dir)

        #add libraries
        libraries = get_libraries(libout, libs)

        #define option
        options = validate_options(option)

        # validate files to compile
        source_files = collect_sources(comp_dir, src, files)

        #only compile when there are files to compile
        if source_files:
            # Compile the program
            compile_program(incdir, libraries, compiler, type, source_files, output_path, options)
        else:
            print (f"no files to compile obj {obj}, skipping")


def main():
    # Setup argument parser
    parser = setup_parser()
    args = parser.parse_args()

    # Show help if no directories are provided
    if not args.directories:
        print("No directories provided, nothing to compile.")
    
    print("Current dir:", current_dir)
    print("Parent dir:", parent_dir)

    #prepare output directories for pro
    prepare_directories(binout)
    prepare_directories(libout)
    #check compiler
    compiler = detect_compiler()

    #process each directory inputs
    for objdir in args.directories:
        #search for compile directory
        comp_dir = check_compile_directory(parent_dir,objdir)
        if not comp_dir : next
        # process bld file
        bldfilevalid, objdic, typdic, srcdic, filedic, libdic, optdic =  process_bldfile(comp_dir)
        if not bldfilevalid : next
        #now compile all obj in the bldfile
        build_program(parent_dir, comp_dir, binout, libout, compiler, objdic, typdic, srcdic, filedic, libdic, optdic)


if __name__ == "__main__":
    main()
    sys.exit()
