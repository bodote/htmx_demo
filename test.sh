#!/usr/bin/env -S java --source 21

import java.time.LocalDate;
import java.util.Random;
import java.util.Scanner;

public class HelloCLI {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Random random = new Random();
        System.out.println("Welcome to the Java CLI. Type 'help' for a list of commands or 'exit' to quit.");

        while (true) {
            System.out.print("Command> ");
            String command = scanner.nextLine().trim().toLowerCase();

            switch (command) {
                case "greet" -> System.out.println("Hello, Java enthusiast!");
                case "date" -> System.out.println("Today's date: " + LocalDate.now());
                case "time" -> System.out.println("Current time: " + java.time.LocalTime.now());
                case "random" -> System.out.println("Random number (1-100): " + (random.nextInt(100) + 1));
                case "add" -> {
                    System.out.print("Enter first number: ");
                    double num1 = scanner.nextDouble();
                    System.out.print("Enter second number: ");
                    double num2 = scanner.nextDouble();
                    scanner.nextLine(); // Consume the newline
                    System.out.println("Result: " + (num1 + num2));
                }
                case "multiply" -> {
                    System.out.print("Enter first number: ");
                    double num1 = scanner.nextDouble();
                    System.out.print("Enter second number: ");
                    double num2 = scanner.nextDouble();
                    scanner.nextLine(); // Consume the newline
                    System.out.println("Result: " + (num1 * num2));
                }
                case "help" -> {
                    System.out.println("""
                        Available commands:
                        - greet: Prints a friendly greeting.
                        - date: Displays today's date.
                        - time: Displays the current time.
                        - random: Generates a random number between 1 and 100.
                        - add: Adds two numbers.
                        - multiply: Multiplies two numbers.
                        - help: Shows this help message.
                        - exit: Exits the program.
                        """);
                }
                case "exit" -> {
                    System.out.println("Exiting... Goodbye!");
                    return; // Terminate the program
                }
                default -> System.out.println("Unknown command: " + command + ". Type 'help' for a list of commands.");
            }
        }
    }
}