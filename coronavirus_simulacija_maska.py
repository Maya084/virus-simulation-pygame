import pygame, sys
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255,255,255)
BLUE = (125, 200, 227)
GREEN = (85, 217, 91)
PURPLE = (162, 125, 227)
GREY = (200,200,200) #(230, 230, 230) #(59, 60, 64)
YELLOW = (190, 175, 50)
RED = (255, 0, 0)
DARK_BLUE = (9, 14, 59)
BACKGROUND = DARK_BLUE

COVID_19 = {
    "Populacija": 300,
    "Zarazeni": 1,
    "Stapka_Na_Smrt": 0.05,
    "Broj_Vo_Izolacija": 150,
    "Denovi_Lekuvanje": 14,
    "Maska" : True
}


class Tocka(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BLACK, radius=5, velocity=[0, 0], randomize=False):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.killswitch_on = False
        self.ozdraven = False
        self.randomize = randomize

        self.WIDTH = width
        self.HEIGHT = height

    def update(self):

        self.pos += self.vel
        x, y = self.pos

        # granici na tockite

        if x < 0:
            self.pos[0] = self.WIDTH
            x = self.WIDTH
        if x > self.WIDTH:
            self.pos[0] = 0
            x = 0
        if y < 0:
            self.pos[1] = self.HEIGHT
            y = self.HEIGHT
        if y > self.HEIGHT:
            self.pos[1] = 0
            y = 0

        self.rect.x = x
        self.rect.y = y

        vel_norm = np.linalg.norm(self.vel)
        if vel_norm > 3:
            self.vel /= vel_norm

        if self.randomize:
            self.vel += np.random.rand(2) * 2 - 1

        if self.killswitch_on:
            self.cycles_to_fate -= 1

            if self.cycles_to_fate <= 0:
                self.killswitch_on = False
                pomosen_broj = np.random.rand()
                if self.stapka_na_smrt > pomosen_broj:
                    self.kill()
                else:
                    self.ozdraven = True

    def respawn(self, color, radius=5):
        return Tocka(self.rect.x, self.rect.y, self.WIDTH, self.HEIGHT, color=color, velocity=self.vel,)
        
    def killswitch(self, cycles_to_fate=75, stapka_na_smrt=0.1):
        self.killswitch_on = True
        self.cycles_to_fate = cycles_to_fate
        self.stapka_na_smrt = stapka_na_smrt


class Simulation:
    def __init__(self, width=600, height=480, sub_width=200):
        self.WIDTH = width
        self.HEIGHT = height
        self.Maska = False
        self.container_podlozni = pygame.sprite.Group()
        self.container_zarazeni = pygame.sprite.Group()
        self.container_ozdraveni = pygame.sprite.Group()
        self.container_site = pygame.sprite.Group()

        self.n_podlezni = 20
        self.n_zarazeni = 1
        self.n_vo_izolacija = 0
        self.T = 1000
        self.cycles_to_fate = 75
        self.stapka_na_smrt = 0.04
        self.sub_width = sub_width
        self.pozicija_dijagram = self.WIDTH-self.sub_width


        self.den = 0

    def start(self, randomize=False):
        
        self.N = (self.n_podlezni + self.n_zarazeni + self.n_vo_izolacija)

        pygame.init()
        screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])

        for i in range(self.n_podlezni):
            x = np.random.randint(0, self.pozicija_dijagram - 5)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            tocka = Tocka(x, y, self.pozicija_dijagram - 5, self.HEIGHT, color=BLUE, velocity=vel, randomize=randomize,)
            
            self.container_podlozni.add(tocka)
            self.container_site.add(tocka)

        for i in range(self.n_vo_izolacija):
            x = np.random.randint(0, self.pozicija_dijagram - 5)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = [0, 0]
            tocka = Tocka(x, y, self.pozicija_dijagram - 5, self.HEIGHT, color=BLUE, velocity=vel, randomize=False,)
            self.container_podlozni.add(tocka)
            self.container_site.add(tocka)

        for i in range(self.n_zarazeni):
            x = np.random.randint(0, self.pozicija_dijagram - 5)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            tocka = Tocka(x, y, self.pozicija_dijagram - 5, self.HEIGHT, color=RED, velocity=vel, randomize=randomize,)
            self.container_zarazeni.add(tocka)
            self.container_site.add(tocka)

        vtor_del = pygame.Surface((self.sub_width, self.HEIGHT))
        vtor_del.fill(WHITE)

        statistika = pygame.Surface((self.sub_width, self.HEIGHT // 2))
        statistika.fill(GREY)
        #statistika.set_alpha(230)
        
        statistika_pozicija = (self.pozicija_dijagram, 0)

        clock = pygame.time.Clock()

        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.container_site.update()

            screen.fill(BACKGROUND)

            # Update na statistika dijagramo
            statistika_visina = statistika.get_height()
            statistika_sirina = statistika.get_width()
            n_momentalno_zarazeni = len(self.container_zarazeni)
            n_momentalna_populacija = len(self.container_site)
            n_momentalno_ozdraveni = len(self.container_ozdraveni)
            t = int((i / self.T) * statistika_sirina)
            y_inficirani = int(statistika_visina - (n_momentalno_zarazeni / n_momentalna_populacija) * statistika_visina)
            y_pocinati = int(((self.N - n_momentalna_populacija) / self.N) * statistika_visina)
            y_ozdraveni = int((n_momentalno_ozdraveni / n_momentalna_populacija) * statistika_visina)
            dijagram = pygame.PixelArray(statistika)
            dijagram[t, y_inficirani:] = pygame.Color(*RED)
            dijagram[t, :y_pocinati] = pygame.Color(*BLACK)
            dijagram[t, y_pocinati : y_pocinati + y_ozdraveni] = pygame.Color(*YELLOW)

            #novi zarazuvanja
            zarazuvanje = 50
            pom_bool = True
            random_broj = np.random.randint(0, 100)
            if (self.Maska == True):
                zarazuvanje = 2
            else:
                zarazuvanje = 90

            if (random_broj <= zarazuvanje):
                pom_bool = True
            else:
                pom_bool = False

            collision_group = pygame.sprite.groupcollide(self.container_podlozni, self.container_zarazeni,pom_bool,False,)

            if(pom_bool):
                for tocka in collision_group:
                    nova_tocka = tocka.respawn(RED)
                    nova_tocka.vel *= -1
                    nova_tocka.killswitch(self.cycles_to_fate, self.stapka_na_smrt)
                    self.container_zarazeni.add(nova_tocka)
                    self.container_site.add(nova_tocka)
                

            # ako ima ozdraveni
            ozdraveni = []
            for tocka in self.container_zarazeni:
                if tocka.ozdraven:
                    nova_tocka = tocka.respawn(YELLOW)
                    self.container_ozdraveni.add(nova_tocka)
                    self.container_site.add(nova_tocka)
                    ozdraveni.append(tocka)

            if len(ozdraveni) > 0:
                self.container_zarazeni.remove(*ozdraveni)
                self.container_site.remove(*ozdraveni)

            self.container_site.draw(screen)

            del dijagram
            statistika.unlock()
            screen.blit(vtor_del, statistika_pozicija)
            screen.blit(statistika, statistika_pozicija)
            
            #tekst prikaz
            font = pygame.font.SysFont('Calibri', 27)
            def render_multi_line(text, x, y, fsize):
                lines = text.splitlines()
                for i, l in enumerate(lines):
                    screen.blit(font.render(l, 0, BLACK), (x, y + fsize * i))
            
            populacija_tekst = "Популација: " + str(self.N) + "\n\n"
            zarazeni_tekst = "Заразени: " + (str)(n_momentalno_zarazeni + y_ozdraveni + y_pocinati) #vkupno slucai do sega
             
            aktivni_slucai_tekst = "\nАктивни случаи: " + str(n_momentalno_zarazeni)
            izlekuvani_tekst = "\nИзлекувани: " + str(y_ozdraveni)
            smrtni_slucai_tekst = "\nСмртни случаи: "+ str(y_pocinati)
            if (i % 15 == 0):
                self.den += 1
            
            den_tekst = "Ден: " + (str)(self.den) + "\n"
            
            tekst = den_tekst + populacija_tekst + zarazeni_tekst + aktivni_slucai_tekst + izlekuvani_tekst + smrtni_slucai_tekst

            #pozicija tekst
            pozicija_x_tekst = self.WIDTH-self.sub_width+15
            pozicija_y_tekst = self.HEIGHT/2+25
            render_multi_line(text = tekst, x=pozicija_x_tekst, y=pozicija_y_tekst, fsize=35)
            #zaboleni (vkupno), izlekuvani, smrtni slucai, aktivni slucai, populacija
            #screen.blit(img, (900, 325))
            
            pygame.display.flip()

            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    covid = Simulation(1250, 650, 350)
    covid.N = COVID_19["Populacija"]
    covid.n_vo_izolacija = COVID_19["Broj_Vo_Izolacija"]
    covid.n_zarazeni = COVID_19["Zarazeni"]
    covid.n_podlezni = covid.N - covid.n_vo_izolacija - covid.n_zarazeni
    covid.cycles_to_fate = COVID_19["Denovi_Lekuvanje"] * 15
    covid.stapka_na_smrt = COVID_19["Stapka_Na_Smrt"]
    covid.Maska = COVID_19["Maska"]
    covid.start(randomize=True)