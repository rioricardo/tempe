import os
import subprocess
import sys
import platform
import shutil


# Get the current script path
current_dir = os.path.dirname(__file__)
# Get the parent directory
parent_dir = os.path.dirname(current_dir)

bindir = os.path.join(parent_dir,'bin')
libdir = os.path.join(parent_dir,'lib')

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

def get_binary_name(prog_name,type):
    """Get the appropriate binary name based on the operating system."""
    if type == 'prog':
        progname = f"{prog_name}.exe" if platform.system() == "Windows" else prog_name
        return os.path.join(bindir,progname)
    elif type == 'lib':
        libname = f"lib{prog_name}.dll" if platform.system() == "Windows" else f"lib{prog_name}.so"
        return os.path.join(libdir,libname)
    else:
        print(f"Error: unknown type of object {prog_name}")
        sys.exit(1)

def load_bldfile(bldfilename):
    """Load and parse the build file, returning program configuration dictionaries."""
    objdic, typdic, filedic, libdic, optdic = {}, {}, {}, {}, {}
    try:
        with open(bldfilename, "r") as bldfile:
            for line in bldfile:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if '=' in line:
                    id, value = line.split('=', maxsplit=1)
                    if id == 'prog':
                        objdic[value] = value
                        typdic[value] = 'prog'
                        obj = value
                    elif id == 'lib':
                        objdic[value] = value
                        typdic[value] = 'lib'
                        obj = value
                    elif id == 'file':
                        filedic[obj] = value
                    elif id == 'libraries':
                        libdic[obj] = value
                    elif id == 'option':
                        optdic[obj] = value
    except FileNotFoundError:
        print(f"Error: {bldfilename} does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {bldfilename}: {e}")
        sys.exit(1)

    return objdic, typdic, filedic, libdic, optdic

def prepare_directories(bindir):
    """Ensure the binary directory exists, creating it if necessary."""
    if not bindir:
        raise ValueError("Binary directory path is missing.")
    try:
        os.makedirs(bindir, exist_ok=True)
    except Exception as e:
        print(f"Error creating binary directory '{bindir}': {e}")
        sys.exit(1)

def validate_sources(srcdir, files):
    """Validate that the source directory and files exist."""
    if not os.path.isdir(srcdir):
        print(f"Error: Source directory '{srcdir}' does not exist.")
        sys.exit(1)
    source_files = [os.path.join(srcdir, f) for f in files.split(';') if os.path.isfile(os.path.join(srcdir, f))]
    if not source_files:
        print("Error: No valid source files found.")
        sys.exit(1)
    return source_files

def validate_options(options):
    if (options):
        return ' '.join(options.split(';'))
    else:
        return None

def compile_program(compiler, type, source_files, output_path, libs, options):
    """Compile the program using the specified compiler and source files."""
    incdir = "-I" + os.path.join(parent_dir)
    custlib = "-L" + os.path.join(libdir)
    if (libs):
        libraries = [f"-l{l}" for l in libs.split(';')]
        libraries = [custlib] + libraries + [f"-Wl,-rpath,{libdir}"]
    if type == 'prog':
        compile_command = [compiler] + source_files + libraries + [opt for opt in [options, incdir, "-g", "-o", output_path] if opt]
    elif type == 'lib':
        compile_command = [compiler] + source_files + [opt for opt in [incdir, options, "-fPIC", "-shared","-g", "-o", output_path] if opt]
    else:
        print(f"Error: unknown type of object {output_path}")
        sys.exit(1)
    try:
        print(f"Compiling {output_path}...")
        print(f"Compile command {compile_command}...")
        subprocess.run(compile_command, check=True)
        print(f"Build successful! Binary created at {output_path}")
    except subprocess.CalledProcessError:
        print("Error: Compilation failed.")
        sys.exit(1)


def build_program(objdir,parent_dir,bldfilename="Bldfile"):

    objdir = os.path.join(parent_dir, objdir)

    if not os.path.isdir(objdir):
        print(f"invalid program or library directory '{objdir}'.")
        return
    
    bldfile = os.path.join(objdir,bldfilename)
    objdic, typdic, filedic, libdic, optdic = load_bldfile(bldfile)
    compiler = detect_compiler()

    for obj in objdic:
        type = typdic.get(obj)
        output_path = get_binary_name(obj,type)
        files = filedic.get(obj)
        option = optdic.get(obj)
        libs = libdic.get(obj)

        if not files:
            print(f"Error: No source files listed for program '{obj}'.")
            sys.exit(1)

        # Prepare directories and validate files
        source_files = validate_sources(objdir, files)

        #define option
        options = validate_options(option)

        # Compile the program
        compile_program(compiler, type, source_files, output_path, libs, options)

def read_arguments(argv):  
    objcomp = []  
    if len(argv) > 1:
        objcomp = argv[1:]
        print(f"Compile: {objcomp}")
    else:
        print("Nothing to compile")
    return objcomp


def main():
    print("Current dir:", current_dir)
    print("Parent dir:", parent_dir)
    prepare_directories(bindir)
    prepare_directories(libdir)

    objcomp = read_arguments(sys.argv)
    
    for objdir in objcomp:
        build_program(objdir,parent_dir)

    
if __name__ == "__main__":
    main()
