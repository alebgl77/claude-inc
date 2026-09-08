// Compiled locally by install.ps1. Paths are embedded; no runtime sidecar.
using System;
using System.Diagnostics;
using System.Text;

internal static class CompanyLauncher
{
    private const string BashPathBase64 = "__BASH_PATH_BASE64__";
    private const string CompanyPathBase64 = "__COMPANY_PATH_BASE64__";

    internal static string QuoteWindowsArgument(string value)
    {
        var result = new StringBuilder();
        result.Append('"');
        int slashes = 0;
        foreach (char character in value)
        {
            if (character == '\\') { slashes++; continue; }
            if (character == '"')
            {
                result.Append('\\', slashes * 2 + 1);
                result.Append('"');
            }
            else
            {
                result.Append('\\', slashes);
                result.Append(character);
            }
            slashes = 0;
        }
        result.Append('\\', slashes * 2);
        result.Append('"');
        return result.ToString();
    }

    private static int Main(string[] arguments)
    {
        try
        {
            string bash = Encoding.UTF8.GetString(Convert.FromBase64String(BashPathBase64));
            string company = Encoding.UTF8.GetString(Convert.FromBase64String(CompanyPathBase64));
            var command = new StringBuilder(QuoteWindowsArgument("-l"));
            command.Append(' ').Append(QuoteWindowsArgument(company));
            foreach (string argument in arguments)
                command.Append(' ').Append(QuoteWindowsArgument(argument));
            var start = new ProcessStartInfo
            {
                FileName = bash,
                Arguments = command.ToString(),
                WorkingDirectory = Environment.CurrentDirectory,
                UseShellExecute = false,
                RedirectStandardInput = false,
                RedirectStandardOutput = false,
                RedirectStandardError = false
            };
            using (Process child = Process.Start(start))
            {
                if (child == null) throw new InvalidOperationException();
                child.WaitForExit();
                return child.ExitCode;
            }
        }
        catch
        {
            Console.Error.WriteLine("company: unable to start the installed Bash CLI. Check Git for Windows and reinstall the company launcher.");
            return 1;
        }
    }
}
