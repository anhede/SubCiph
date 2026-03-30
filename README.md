# SubCiph
A TUI application for interactively deciphering simple substitution ciphers.

<script src="https://asciinema.org/a/879075.js" id="asciicast-879075" async="true"></script>

## Usage
The application uses a wordlist to show recommendations of words matching the pattern of currently locked letters. This is optional but recommended, and is supplied using the -w argument. The order of the wordlist matches the order of recommendations, thus a frequency ordered wordlist is recommended, e.g. https://github.com/first20hours/google-10000-english/

`subciph.py [CIPHERTEXT_FILE] -w (WORDLIST)`

## PRs
If you'd like to add functionality to the project, there are several features which could be promising:

- Vigenère Cipher: Supporting interactive deciphering of Vigenère ciphers would be great, especially if possible to chain together with a simple substitution later.
- Main Menu: Adding a main-menu which supports moving between tools, e.g. Vigenère and Simple Substitution would allow chaining encryptions.
