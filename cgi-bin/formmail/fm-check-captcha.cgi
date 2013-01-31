#!/usr/bin/perl
##############################################################################
# By BumbleBeeWare.com 2006
# Simple CAPTCHA using static premade images
# check-captcha.cgi
##############################################################################

# Altered by Chris Michaelis in Apr 2008 to make a callable function

sub CleanUpOldFiles()
{
	$tempdir = "./tmp";

	# remove all old temp files
	# this keeps the director clean without setting up a cron job
	opendir TMPDIR, "$tempdir"; 
	@alltmpfiles = readdir TMPDIR;

	foreach $oldtemp (@alltmpfiles)
	{
		$age = 0;
		$age = (stat("$tempdir/$oldtemp"))[9];
		# if age is more than 300 seconds or 5 minutes	
		if ((time - $age) > 300){unlink "$tempdir/$oldtemp";}
	}
}

sub CheckCaptcha()
{
	$tempdir = "./tmp";

	&form_parse;

	# lets block direct access that is not via the form post
	if ($ENV{"REQUEST_METHOD"} ne "POST"){&nopost;}

	# open the temp datafile for current user based on ip
	$tempfile = "$tempdir/$ENV{'REMOTE_ADDR'}";
	open (TMPFILE, "<$tempfile")|| ($nofile = 1);
	(@tmpfile) = <TMPFILE>;
	close TMPFILE;

	# if no matching ip file check for a cookie match
	# this will compensate for AOL proxy servers accessing images
	if ($nofile == 1)
	{
		$cookieip = $ENV{HTTP_COOKIE};
		$cookieip =~ /checkme=([^;]*)/;
		$cookieip = $1;
		if ($cookieip ne "")
		{
			$tempfile = "$tempdir/$cookieip";
			open (TMPFILE, "<$tempdir/$cookieip")|| &nofile;
			(@tmpfile) = <TMPFILE>;
			close TMPFILE;
		}
	}

	$imagetext = $tmpfile[0];
	chomp $imagetext;
	# set the form input to lower case
	$a = lc($_[0]);

	# compare the form input with the file text
	if ($a ne "$imagetext")
	{
		# Don't clean up yet - the user will likely be returning soon
		return 0;
	}

	# now delete the temp file so it cannot be used again by the same user
	unlink "$tempfile";
	CleanUpOldFiles();

	# if no error continue with the program
	return 1;
}

sub nofile {
	
print "Content-type: text/html\n\n";
print "No file found for verification.";	
exit;	
}


sub nopost {
	
print "Content-type: text/html\n\n";
print "Method not allowed, input must be via a form post.";	
exit;	
}

sub form_parse  {
	read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	@pairs = split(/&/, $buffer);

	foreach $pair (@pairs)
	{
    	($name, $value) = split(/=/, $pair);
    	$value =~ tr/+/ /;
    	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    	$FORM{$name} = $value;
}}

1;
