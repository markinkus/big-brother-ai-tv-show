import { create } from "zustand";

type NeuralHouseStore = {
  seasonId: number;
  vipRoom: string | null;
  setSeasonId: (seasonId: number) => void;
  setVipRoom: (vipRoom: string | null) => void;
};

export const useNeuralHouseStore = create<NeuralHouseStore>((set) => ({
  seasonId: 1,
  vipRoom: null,
  setSeasonId: (seasonId) => set({ seasonId }),
  setVipRoom: (vipRoom) => set({ vipRoom }),
}));

