%% Extract Teager energy over time.

function [TE] = teager(sig)
TE = 1:1:length(sig)-2;

%http://folk.uio.no/eivindkv/ek-thesis-2003-05-12-final-2.pdf
for n = 2:1:(length(sig)-1)
    TE(n-1) = abs(sig(n))^2 - sig(n+1)*(sig(n-1));
end