import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

/**
 * Application de gestion de loto français (1 à 90) en Java Swing.
 */
public class LotoApp extends JFrame {
    private static final Color PANEL = new Color(17, 24, 39);
    private static final Color PANEL_ALT = new Color(31, 41, 55);
    private static final Color TEXT = new Color(249, 250, 251);
    private static final Color MUTED = new Color(203, 213, 225);
    private static final Color ACCENT = new Color(245, 158, 11);
    private static final Color SUCCESS = new Color(34, 197, 94);
    private static final Color DANGER = new Color(239, 68, 68);

    private final Set<Integer> drawnNumbers = new LinkedHashSet<>();
    private final JLabel lastLabel = new JLabel("--", SwingConstants.CENTER);
    private final JLabel secondLabel = new JLabel("--", SwingConstants.CENTER);
    private final JLabel thirdLabel = new JLabel("--", SwingConstants.CENTER);
    private final JTextField entryField = new JTextField();
    private final JTextArea historyArea = new JTextArea();
    private final JLabel gainLabel = new JLabel("Aucun gain annoncé");
    private final JButton[] gainButtons = new JButton[3];
    private final JButton[][] gridButtons = new JButton[9][10];

    private JButton addButton;
    private JButton randomButton;
    private JButton resetButton;

    private boolean animationRunning = false;
    private final Random random = new Random();

    public LotoApp() {
        super("Loto 1-90 (Java)");
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        setMinimumSize(new Dimension(1180, 760));
        setSize(1366, 820);
        setLocationRelativeTo(null);

        setContentPane(new GradientPanel());
        getContentPane().setLayout(new BorderLayout());

        JPanel main = new JPanel(new GridBagLayout());
        main.setOpaque(false);
        main.setBorder(new EmptyBorder(20, 24, 20, 24));
        getContentPane().add(main, BorderLayout.CENTER);

        buildLayout(main);
        refreshRecentLabels();
        refreshHistory();
    }

    private void buildLayout(JPanel main) {
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridy = 0;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.weighty = 1;

        JPanel left = createPanel(PANEL);
        JPanel right = createPanel(PANEL_ALT);

        gbc.gridx = 0;
        gbc.weightx = 2;
        gbc.insets = new Insets(0, 0, 0, 12);
        main.add(left, gbc);

        gbc.gridx = 1;
        gbc.weightx = 3;
        gbc.insets = new Insets(0, 12, 0, 0);
        main.add(right, gbc);

        buildLeftPanel(left);
        buildRightPanel(right);
    }

    private JPanel createPanel(Color color) {
        JPanel panel = new JPanel();
        panel.setBackground(color);
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(new EmptyBorder(16, 16, 16, 16));
        return panel;
    }

    private void buildLeftPanel(JPanel left) {
        JLabel title = new JLabel("🎱 LOTO FRANÇAIS", SwingConstants.CENTER);
        title.setForeground(TEXT);
        title.setFont(new Font("Segoe UI", Font.BOLD, 30));
        title.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subtitle = new JLabel("Version Java Swing - gestion complète", SwingConstants.CENTER);
        subtitle.setForeground(MUTED);
        subtitle.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        subtitle.setAlignmentX(Component.CENTER_ALIGNMENT);

        left.add(title);
        left.add(Box.createVerticalStrut(6));
        left.add(subtitle);
        left.add(Box.createVerticalStrut(16));

        JPanel recents = createSectionPanel(PANEL_ALT);
        recents.setLayout(new BoxLayout(recents, BoxLayout.Y_AXIS));
        lastLabel.setForeground(ACCENT);
        lastLabel.setFont(new Font("Segoe UI", Font.BOLD, 126));
        secondLabel.setForeground(TEXT);
        secondLabel.setFont(new Font("Segoe UI", Font.BOLD, 52));
        thirdLabel.setForeground(MUTED);
        thirdLabel.setFont(new Font("Segoe UI", Font.PLAIN, 34));
        recents.add(lastLabel);
        recents.add(secondLabel);
        recents.add(thirdLabel);
        left.add(recents);
        left.add(Box.createVerticalStrut(12));

        JPanel manual = createSectionPanel(PANEL);
        manual.setLayout(new BorderLayout(8, 8));
        JLabel manualTitle = new JLabel("Ajouter un numéro (1 à 90)");
        manualTitle.setForeground(TEXT);
        manualTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        manual.add(manualTitle, BorderLayout.NORTH);

        entryField.setFont(new Font("Segoe UI", Font.BOLD, 24));
        entryField.setHorizontalAlignment(SwingConstants.CENTER);
        entryField.setBackground(new Color(229, 231, 235));
        entryField.setForeground(new Color(17, 24, 39));
        entryField.addActionListener(e -> addFromEntry());

        addButton = createButton("Ajouter", SUCCESS, e -> addFromEntry());
        JPanel entryLine = new JPanel(new BorderLayout(8, 0));
        entryLine.setOpaque(false);
        entryLine.add(entryField, BorderLayout.CENTER);
        entryLine.add(addButton, BorderLayout.EAST);
        manual.add(entryLine, BorderLayout.CENTER);
        left.add(manual);
        left.add(Box.createVerticalStrut(10));

        JPanel actionRow = new JPanel(new GridLayout(1, 2, 8, 0));
        actionRow.setOpaque(false);
        randomButton = createButton("Tirage aléatoire", ACCENT, e -> startRandomAnimation());
        resetButton = createButton("Reset", DANGER, e -> reset());
        actionRow.add(randomButton);
        actionRow.add(resetButton);
        left.add(actionRow);
        left.add(Box.createVerticalStrut(10));

        JPanel gains = createSectionPanel(PANEL);
        gains.setLayout(new BorderLayout(0, 8));

        JLabel gainTitle = new JLabel("Annonce des gains");
        gainTitle.setForeground(TEXT);
        gainTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        gains.add(gainTitle, BorderLayout.NORTH);

        JPanel gainRow = new JPanel(new GridLayout(1, 3, 8, 0));
        gainRow.setOpaque(false);
        gainButtons[0] = createButton("Quine simple", new Color(99, 102, 241), e -> setGain("Quine simple"));
        gainButtons[1] = createButton("Quine double", new Color(139, 92, 246), e -> setGain("Quine double"));
        gainButtons[2] = createButton("Carton plein", new Color(236, 72, 153), e -> setGain("Carton plein"));
        gainRow.add(gainButtons[0]);
        gainRow.add(gainButtons[1]);
        gainRow.add(gainButtons[2]);
        gains.add(gainRow, BorderLayout.CENTER);

        gainLabel.setForeground(ACCENT);
        gainLabel.setFont(new Font("Segoe UI", Font.BOLD, 15));
        gains.add(gainLabel, BorderLayout.SOUTH);

        left.add(gains);
        left.add(Box.createVerticalStrut(10));

        JPanel historyPanel = createSectionPanel(PANEL);
        historyPanel.setLayout(new BorderLayout(0, 8));
        JLabel historyTitle = new JLabel("Historique des numéros tirés");
        historyTitle.setForeground(TEXT);
        historyTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        historyPanel.add(historyTitle, BorderLayout.NORTH);

        historyArea.setEditable(false);
        historyArea.setLineWrap(true);
        historyArea.setWrapStyleWord(true);
        historyArea.setBackground(new Color(11, 18, 32));
        historyArea.setForeground(TEXT);
        historyArea.setFont(new Font("Consolas", Font.PLAIN, 14));
        historyArea.setBorder(new EmptyBorder(10, 10, 10, 10));
        historyPanel.add(new JScrollPane(historyArea), BorderLayout.CENTER);

        left.add(historyPanel);
    }

    private void buildRightPanel(JPanel right) {
        right.setLayout(new BorderLayout(0, 10));

        JLabel title = new JLabel("Grille complète 1 à 90", SwingConstants.LEFT);
        title.setForeground(TEXT);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        right.add(title, BorderLayout.NORTH);

        JPanel grid = new JPanel(new GridLayout(9, 10, 6, 6));
        grid.setOpaque(false);

        for (int number = 1; number <= 90; number++) {
            int row = (number - 1) / 10;
            int col = (number - 1) % 10;
            JButton cell = new JButton(String.valueOf(number));
            cell.setFocusable(false);
            cell.setEnabled(false);
            cell.setBackground(new Color(17, 24, 39));
            cell.setForeground(TEXT);
            cell.setFont(new Font("Segoe UI", Font.BOLD, 20));
            cell.setBorder(BorderFactory.createLineBorder(new Color(55, 65, 81), 1));
            grid.add(cell);
            gridButtons[row][col] = cell;
        }

        right.add(grid, BorderLayout.CENTER);
    }

    private JPanel createSectionPanel(Color bg) {
        JPanel panel = new JPanel();
        panel.setBackground(bg);
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));
        return panel;
    }

    private JButton createButton(String text, Color color, java.awt.event.ActionListener action) {
        JButton button = new JButton(text);
        button.setFocusPainted(false);
        button.setFont(new Font("Segoe UI", Font.BOLD, 12));
        button.setBackground(color);
        button.setForeground(new Color(17, 24, 39));
        button.setBorder(new EmptyBorder(10, 12, 10, 12));
        button.addActionListener(action);
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseEntered(java.awt.event.MouseEvent e) {
                if (button.isEnabled()) {
                    button.setBackground(shade(color, 0.1f));
                }
            }

            @Override
            public void mouseExited(java.awt.event.MouseEvent e) {
                button.setBackground(color);
            }
        });
        return button;
    }

    private void addFromEntry() {
        if (animationRunning) {
            return;
        }

        String raw = entryField.getText().trim();
        if (raw.isEmpty()) {
            return;
        }
        int number;
        try {
            number = Integer.parseInt(raw);
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Veuillez saisir un entier entre 1 et 90.", "Saisie invalide", JOptionPane.WARNING_MESSAGE);
            return;
        }
        addNumber(number);
    }

    private boolean addNumber(int number) {
        if (number < 1 || number > 90) {
            JOptionPane.showMessageDialog(this, "Le numéro doit être compris entre 1 et 90.", "Hors limite", JOptionPane.WARNING_MESSAGE);
            return false;
        }
        if (drawnNumbers.contains(number)) {
            JOptionPane.showMessageDialog(this, "Le numéro " + number + " a déjà été tiré.", "Doublon", JOptionPane.WARNING_MESSAGE);
            return false;
        }

        drawnNumbers.add(number);
        entryField.setText("");
        refreshRecentLabels();
        refreshHistory();
        markNumber(number);
        pulseLastNumber();

        if (drawnNumbers.size() == 90) {
            JOptionPane.showMessageDialog(this, "Tous les numéros ont été tirés.", "Terminé", JOptionPane.INFORMATION_MESSAGE);
        }
        return true;
    }

    private void startRandomAnimation() {
        if (animationRunning) {
            return;
        }

        List<Integer> remaining = getRemainingNumbers();
        if (remaining.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Il ne reste plus de numéro à tirer.", "Terminé", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        animationRunning = true;
        setControlsEnabled(false);

        int finalNumber = remaining.get(random.nextInt(remaining.size()));
        animateRoll(0, 3500, finalNumber, 40, 320);
    }

    private void animateRoll(int elapsed, int duration, int finalNumber, int minDelay, int maxDelay) {
        double progress = Math.min((double) elapsed / duration, 1.0);

        if (progress >= 1.0) {
            lastLabel.setText(String.format("%02d", finalNumber));
            lastLabel.setForeground(ACCENT);
            addNumber(finalNumber);
            animationRunning = false;
            setControlsEnabled(true);
            return;
        }

        List<Integer> remaining = getRemainingNumbers();
        int rollingNumber = remaining.get(random.nextInt(remaining.size()));
        lastLabel.setText(String.format("%02d", rollingNumber));
        lastLabel.setForeground(new Color(253, 230, 138));

        int delay = (int) (minDelay + (maxDelay - minDelay) * (progress * progress));
        Timer timer = new Timer(delay, (ActionEvent e) -> animateRoll(elapsed + delay, duration, finalNumber, minDelay, maxDelay));
        timer.setRepeats(false);
        timer.start();
    }

    private List<Integer> getRemainingNumbers() {
        List<Integer> remaining = new ArrayList<>();
        for (int i = 1; i <= 90; i++) {
            if (!drawnNumbers.contains(i)) {
                remaining.add(i);
            }
        }
        return remaining;
    }

    private void setGain(String gainName) {
        gainLabel.setText("Gain annoncé : " + gainName);
    }

    private void reset() {
        if (animationRunning) {
            return;
        }

        drawnNumbers.clear();
        gainLabel.setText("Aucun gain annoncé");
        entryField.setText("");

        for (int i = 1; i <= 90; i++) {
            JButton cell = getCell(i);
            cell.setBackground(new Color(17, 24, 39));
            cell.setForeground(TEXT);
        }

        refreshRecentLabels();
        refreshHistory();
    }

    private void refreshRecentLabels() {
        List<Integer> numbers = new ArrayList<>(drawnNumbers);
        int n = numbers.size();
        lastLabel.setText(n >= 1 ? String.format("%02d", numbers.get(n - 1)) : "--");
        secondLabel.setText(n >= 2 ? String.format("%02d", numbers.get(n - 2)) : "--");
        thirdLabel.setText(n >= 3 ? String.format("%02d", numbers.get(n - 3)) : "--");
        lastLabel.setForeground(ACCENT);
    }

    private void refreshHistory() {
        if (drawnNumbers.isEmpty()) {
            historyArea.setText("Aucun numéro tiré pour le moment.");
            return;
        }

        StringBuilder sb = new StringBuilder();
        for (Integer value : drawnNumbers) {
            if (sb.length() > 0) {
                sb.append(" - ");
            }
            sb.append(String.format("%02d", value));
        }
        historyArea.setText(sb.toString());
    }

    private void markNumber(int number) {
        JButton cell = getCell(number);
        cell.setBackground(SUCCESS);
        cell.setForeground(new Color(5, 46, 22));
        flashCell(cell, 4);
    }

    private JButton getCell(int number) {
        int row = (number - 1) / 10;
        int col = (number - 1) % 10;
        return gridButtons[row][col];
    }

    private void flashCell(JButton cell, int count) {
        if (count <= 0) {
            cell.setBackground(SUCCESS);
            return;
        }

        Color c = cell.getBackground().equals(SUCCESS) ? new Color(134, 239, 172) : SUCCESS;
        cell.setBackground(c);

        Timer timer = new Timer(120, e -> flashCell(cell, count - 1));
        timer.setRepeats(false);
        timer.start();
    }

    private void pulseLastNumber() {
        pulseStep(0, 126);
    }

    private void pulseStep(int index, int baseSize) {
        if (index > 6) {
            lastLabel.setFont(new Font("Segoe UI", Font.BOLD, baseSize));
            return;
        }

        int size = (index % 2 == 0) ? baseSize + 10 : baseSize;
        lastLabel.setFont(new Font("Segoe UI", Font.BOLD, size));

        Timer timer = new Timer(60, e -> pulseStep(index + 1, baseSize));
        timer.setRepeats(false);
        timer.start();
    }

    private void setControlsEnabled(boolean enabled) {
        entryField.setEnabled(enabled);
        addButton.setEnabled(enabled);
        randomButton.setEnabled(enabled);
        resetButton.setEnabled(enabled);
        for (JButton gainButton : gainButtons) {
            gainButton.setEnabled(enabled);
        }
    }

    private static Color shade(Color base, float amount) {
        int r = Math.min(255, (int) (base.getRed() + (255 - base.getRed()) * amount));
        int g = Math.min(255, (int) (base.getGreen() + (255 - base.getGreen()) * amount));
        int b = Math.min(255, (int) (base.getBlue() + (255 - base.getBlue()) * amount));
        return new Color(r, g, b);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new LotoApp().setVisible(true));
    }

    /**
     * Panneau avec fond dégradé vertical.
     */
    private static class GradientPanel extends JPanel {
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
            GradientPaint gp = new GradientPaint(
                    0, 0, new Color(15, 23, 42),
                    0, getHeight(), new Color(29, 78, 216)
            );
            g2.setPaint(gp);
            g2.fillRect(0, 0, getWidth(), getHeight());
            g2.dispose();
        }
    }
}
