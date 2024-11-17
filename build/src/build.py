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
parent_dir = os.path.dirname(parent_dir)

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
    config = {
        'objdic': {},
        'typdic': {},
        'srcdic': {},
        'filedic': {},
        'libdic': {},
        'optdic': {}
    }
    dicname = {
        'dir' : 'srcdic',
        'file' : 'filedic',
        'libraries' : 'libdic',
        'option' : 'optdic'
    }
    obj = None

    try:
        with open(bldfilename, "r") as bldfile:
            for line in bldfile:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse key-value pairs
                if '=' in line:
                    key, value = (part.strip() for part in line.split('=', maxsplit=1))
                    
                    if key in {'prog', 'dynlib', 'statlib'}:
                        obj = value
                        config['objdic'][obj] = value
                        config['typdic'][obj] = key
                    elif key in {'dir', 'file', 'libraries', 'option'}:
                        if obj:
                            config_key = dicname[key]
                            config[config_key][obj] = value
                        else:
                            print(f"No object file found for {key} and {value}")
    except FileNotFoundError:
        print(f"Error: {bldfilename} does not exist.")
    except Exception as e:
        print(f"Error reading {bldfilename}: {e}")

    return config['objdic'], config['typdic'], config['srcdic'], config['filedic'], config['libdic'], config['optdic']


def objects_in_bldfile_valid(bldfile,objdic,typdic):
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
    if not objects_in_bldfile_valid(bldfile, objdic, typdic): 
        bldfilevalid = False
        
    return bldfilevalid, objdic, typdic, srcdic, filedic, libdic, optdic

#end of bldfile processes

#compilation processes

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

def add_include(parent_dir):
    #add includes 
    return "-I" + os.path.join(parent_dir)

# I: program name according to bldfile and the type
def get_binary_name(binout, libout, prog_name, obj_type):
    """Get the appropriate binary name based on the operating system."""
    system_platform = platform.system()
    
    extensions = {
        'prog': {'Windows': '.exe', 'default': ''},
        'dynlib': {'Windows': '.dll', 'Darwin': '.dylib', 'default': '.so'},
        'statlib': {'Windows': '.lib', 'default': '.a'}
    }

    if obj_type not in extensions:
        print(f"Error: unknown type of object {prog_name}")
        return None
    
    ext = extensions[obj_type].get(system_platform, extensions[obj_type]['default'])
    prefix = '' if obj_type == 'prog' else 'lib'
    name = f"{prefix}{prog_name}{ext}"
    
    return os.path.join(binout if obj_type == 'prog' else libout, name)

def get_obj_attributes(binout, libout, obj, typdic, srcdic, filedic, libdic, optdic):
        type = typdic.get(obj)
        output_path = get_binary_name(binout, libout, obj,type)
        src = srcdic.get(obj)
        files = filedic.get(obj)
        option = optdic.get(obj)
        libs = libdic.get(obj)
        return output_path,type,src,files,option,libs


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
    
#procedure to build program
def build_program(parent_dir, comp_dir, binout, libout, compiler, objdic, typdic, srcdic, filedic, libdic, optdic):
    #loop through every single object in objdic
    for obj in objdic:
        output_path,type,src,files,option,libs = get_obj_attributes(binout, libout, obj, typdic, srcdic, filedic, libdic, optdic)
        if not output_path: next
        #add include directory
        incdir = add_include(parent_dir)
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
