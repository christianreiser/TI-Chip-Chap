variable "project_id" {
  default = "chatbot-420"
}

variable "image_tag" {
  description = "The image tag for the chatbot-service"
  type        = string
}

variable "openai_id" {
  description = "The OpenAI API key"
  type        = string
}
