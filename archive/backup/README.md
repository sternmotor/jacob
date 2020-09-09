# Rotation schedule
see sh and ps1 file for implementation so far, plus:
TODO
* do not delete all obsolete directories (from rotation or clear-space)
but keep the newest obsolete one, move into place of actual working dir (timestamp-dir)
and run copy with robocopy (incremental), then    
* implement schedule list for automatic trimming down backups
```
    m:h:d:w:m:y
    0:24:14:6:6:10      60x
    0:4:7:4:5:10        30x
    0:0:5:2:3:10        20x
    0:0:5:2:1:3         10x    
    0:0:3:1:1:0          5x
    0:0:1:1:0:0          2x
    0:0:1:0:0:0          1x
```

For given schedule (user input), run this schedule first and run the fixed schedule above afterwards (if not disabled)



# linux backups rsync vs. Rdiff-backup vs. Borg

See [comparison](https://www.reddit.com/r/linux/comments/42feqz/i_asked_here_for_the_optimal_backup_solution_and/), [Borg documentation](https://borgbackup.readthedocs.io/en/stable/) and [German borg howto](https://thomas-leister.de/server-backups-mit-borg/). Borg only supports push backups while better scaling setup for multiple customers would be pull (where number of parallel running backup runs can be controlled). Notable: deduplication, mount option, target encryption, Hetzner support

Workaround: restricted keys in "authorized_keys" of backup user, allowing backups and append and specified directory access only
```
command="borg serve --restrict-to-path /home/serverbackup/backups/server1 --append-only" ssh-ed25519 AAAAB....
```

Control backup runs 
Servers that share a lot of identical or similar files go into same set. 
the servers in the same set will share 1 repository and will have to run 
backups one after each other (you can tweak --lock-wait so one waits 
until the previous one has finished)

If a server has a unusually high count of files or high amount of 
data, use a separate repo just for that server.

If you back them up into a single repo, you will have to frequently resync the chunks cache on each server and also you can't do backups in parallel to same repo.

* Idea1: let linux server SYSTEM backups run on one repository for high deduplication efficiency (with wait option) and DATA backups on a single repository per server
* Idea2: control backup runs from central backup server by running backups via SSH command from backup Server to client (use same tunnel for data?)




Thin out backups: `borg prune --prefix ...`





I would like to provide some additional information for future readers of this thread - specifically on rsync snapshots, rsnapshot, duplicity, attic and borg.

The simplest thing to do is to rsync from one system to another. Very simple, but the problem is it's just a "dumb mirror" - there is no history, no versions in the past (snapshots in time) and every day you do your rsync, you risk clobbering old data that you won't realize you need until tomorrow.

So the next thing to do is graduate to "rsync snapshots" - sometimes known as "hard link snapshots". The originator of this method was Mike Rubel[2]. What you are doing here is making a hard links only copy of yesterdays backup (which means it takes up no space, since it's just hard links) and then doing your "dumb rsync". Any files that changed will break the hard links and your snapshot from yesterday will take up as much space on disk as (the total size of all files that changed since yesterday). It's very simple, very elegant, and requires no software support or requirements on the remote end - as long as you can ssh to the server and run rsync/cp/rm it will work.

Next step is to stop writing the (very simple) rsync snapshot scripts and let rsnapshot do it for you. We've never recommended this, since the rsync snapshot script is so simple, and rsnapshot requires that you put it on the server side ... so it's not as lightweight or universal. As far as we know, it's terrific, bulletproof software.

(Here is a good spot to point out that Apples "Time Machine" backup tool is nothing but rsync and hard link snapshots - that's all it is. Super simple, super basic - so you and a lot of people you know may have been using rsync snapshots for years without even knowing it)

There's one problem with these methods and that is the resulting, remote backups are not encrypted. Your provider, or host (rsync.net, for instance) can theoretically see your data. If this is a problem, you need something other than rsync.

The answer to this problem since 2006 or so has been duplicity.[3] duplicity is wonderful software, has a long history of stable, well organized development, and we have even contributed funds toward its development in the past. The problem with duplicity is that, due to some design constraints that I am not going to go into, every month or two or three you're going to have to re-upload your entire dataset again. The whole thing. That might not matter to you (small datasets) or it might be a deal killer (multi terabytes over WAN).

So now we come to attic and borg - borg being a more recently and more actively developed fork of attic. attic/borg give you all the network efficiency of rsync (changes only updates over network) and all of the remote-side encryption and variable retention of duplicity (and rdiff-backup) but without any of the gotchas of duplicity. Some folks refer to attic/borg as "the holy grail of network backups"[4].

We[5] are the only remote backup / cloud storage provider with support for attic and borg[6]. However, we are also the only provider running a ZFS based platform[7] on the remote end. This means two things: If you don't require remotely encrypted backups, you can just do a "dumb rsync" to us, completely neglecting any kind of retention, and we will do ZFS snapshots of your data on the server side. It's like having Apples time machine in the cloud. OR, IF YOU DO require remotely encrypted backups, you can just point attic or borg at us and solve the problem that way. Either way, you're getting the one thing nobody else will give you - a plain old unix filesystem, in the cloud, that you can do whatever you want with.