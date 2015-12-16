%% This function is meant to receive the teager energy of a function as the
%  input, and then uses that input in order to determine candidate ranges
%  of times in the signal during which agitation may have occured. Possible
%  candidate ranges are identified by a spikes in the Teager energy. The
%  spikes for candidates of voice can be isolated from spikes of other
%  types by the surrounding signal, which has the presence of much more
%  oscillation than other spikes, such as objects being dropped, etc.

function [Ranges] = TimeIdentifier(sig, Threshold)

%ABS of the sig
sig = abs(sig);
Ranges = struct([]);

%First data point has huge value, I think that is noise most likely
sig(abs(sig)>Threshold) = 1;
sig(sig ~= 1) = 0;

Ranges = sig;

% while (n < length(sig))
%     if (n > Fs*5 && n+Fs*5 < length(sig))
%         Ranges{n} = sig(n-Fs*5:n+Fs*5);
%     elseif (n < Fs*5)
%         Ranges{n} = sig(1:n+Fs*5);
%     elseif (n + Fs*5 > length(sig))
%         Ranges{n} = sig(n-Fs*5:end);
%         break;
%     end
%     
%     n = floor(n + 2.5*Fs);
% end