class Email:
    id = 0
    toAddress = ""
    fromAddress = ""
    subject = ""
    body = ""
    originalEmail = ""

    def __init__(self, id, toAddress, fromAddress,
                 subject, body, originalEmail):
        self.id = id
        self.toAddress = toAddress
        self.fromAddress = fromAddress
        self.subject = subject
        self.body = body
        self.originalEmail = originalEmail

    def __str__(self):
        return " ".join([str(self.id), self.toAddress, self.fromAddress,
                         self.subject, self.body])
