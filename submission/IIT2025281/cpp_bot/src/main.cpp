#include <skeleton/actions.h>
#include <skeleton/constants.h>
#include <skeleton/runner.h>
#include <skeleton/states.h>
#include <iostream>
#include <array>
#include <time.h>

using namespace pokerbots::skeleton;

struct Bot {
  void handleNewRound(GameInfoPtr gameState, RoundStatePtr roundState, int active) {}
  void handleRoundOver(GameInfoPtr gameState, TerminalStatePtr terminalState, int active) {}

  // Helper: Extract the rank of a card (e.g., "Ah" -> 'A')
  char getRank(const std::string& card) {
      return card[0];
  }

  // Helper: Check if we are holding our bounty card
  bool holdsBounty(const std::array<std::string, 2>& myCards, char myBounty) {
      return getRank(myCards[0]) == myBounty || getRank(myCards[1]) == myBounty;
  }

  // Helper: Check if we have a pocket pair
  bool isPocketPair(const std::array<std::string, 2>& myCards) {
      return getRank(myCards[0]) == getRank(myCards[1]);
  }

  // Helper: Evaluate basic pre-flop hand strength
  bool isPremiumPreFlop(const std::array<std::string, 2>& myCards) {
      std::string premiumRanks = "AKQJT9";
      bool card1Premium = premiumRanks.find(getRank(myCards[0])) != std::string::npos;
      bool card2Premium = premiumRanks.find(getRank(myCards[1])) != std::string::npos;
      return isPocketPair(myCards) || (card1Premium && card2Premium);
  }

  Action getAction(GameInfoPtr gameState, RoundStatePtr roundState, int active) {
    auto legalActions = roundState->legalActions();
    int street = roundState->street;  
    auto myCards = roundState->hands[active];   
    int myPip = roundState->pips[active];  
    int oppPip = roundState->pips[1-active]; 
    int continueCost = oppPip - myPip;  
    int potSize = roundState->stacks[active] + roundState->stacks[1-active];
    potSize = (STARTING_STACK * 2) - potSize; 
    char myBounty = roundState->bounties[active];  

    float potOdds = 0.0;
    if (continueCost > 0) {
        potOdds = (float)continueCost / (potSize + continueCost);
    }

    // --- PRE-FLOP LOGIC (Street == 0) ---
    if (street == 0) {
        bool hasBounty = holdsBounty(myCards, myBounty);
        bool isPremium = isPremiumPreFlop(myCards);

        if (hasBounty || isPremium) {
            if (legalActions.find(Action::Type::RAISE) != legalActions.end()) {
                auto raiseBounds = roundState->raiseBounds();
                int raiseAmount = raiseBounds[0] + (raiseBounds[1] - raiseBounds[0]) / 4; 
                return {Action::Type::RAISE, raiseAmount};
            }
            if (legalActions.find(Action::Type::CALL) != legalActions.end()) {
                return {Action::Type::CALL};
            }
        } else {
            if (continueCost > 0 && legalActions.find(Action::Type::FOLD) != legalActions.end()) {
                return {Action::Type::FOLD};
            }
            return {Action::Type::CHECK};
        }
    }

    // --- POST-FLOP LOGIC (Street > 0) ---
    if (continueCost == 0 && legalActions.find(Action::Type::CHECK) != legalActions.end()) {
        return {Action::Type::CHECK};
    }

    if (potOdds > 0.20 && !holdsBounty(myCards, myBounty)) {
        if (legalActions.find(Action::Type::FOLD) != legalActions.end()) {
            return {Action::Type::FOLD};
        }
    }

    if (legalActions.find(Action::Type::CALL) != legalActions.end()) {
        return {Action::Type::CALL};
    }

    return {Action::Type::FOLD};
  }
};

int main(int argc, char *argv[]) {
  srand(time(NULL));
  auto [host, port] = parseArgs(argc, argv);
  runBot<Bot>(host, port);
  return 0;
}
